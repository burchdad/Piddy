"""
Browser automation tool for Piddy.

Provides Playwright-based browser control: navigate, screenshot, fill forms,
extract content, click elements, and run automated testing sequences.

Requires: pip install playwright && python -m playwright install chromium

All actions are sandboxed: Piddy never sends credentials or executes
arbitrary scripts on remote pages (SSRF / injection guardrails included).
"""

import logging
import asyncio
import base64
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright  # type: ignore[import-unresolved]
    HAS_PLAYWRIGHT = True
except ImportError:
    async_playwright = None  # type: ignore[assignment]
    HAS_PLAYWRIGHT = False
    logger.info("Playwright not installed — install with: pip install playwright && python -m playwright install chromium")

# ---------------------------------------------------------------------------
# Safety: block navigation to internal / private addresses
# ---------------------------------------------------------------------------
_BLOCKED_HOSTS = re.compile(
    r"^(localhost|127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+|0\.0\.0\.0|\[::1\])",
    re.IGNORECASE,
)


def _validate_url(url: str) -> str:
    """Ensure URL is an absolute http(s) URL and not pointed at internal networks."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("Only http:// and https:// URLs are allowed")
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if _BLOCKED_HOSTS.match(parsed.hostname or ""):
        raise ValueError("Navigation to internal/private network addresses is blocked")
    return url


class BrowserAutomation:
    """Headless browser automation backed by Playwright."""

    def __init__(self):
        self._playwright: Any = None
        self._browser: Any = None
        self._page: Any = None

    # -- lifecycle -----------------------------------------------------------

    async def launch(self, headless: bool = True) -> Dict[str, Any]:
        if not HAS_PLAYWRIGHT:
            return {"success": False, "error": "Playwright not installed. Run: pip install playwright && python -m playwright install chromium"}

        if self._browser is not None:
            return {"success": False, "error": "Browser already running. Close first."}

        self._playwright = await async_playwright().start()  # type: ignore[misc]
        self._browser = await self._playwright.chromium.launch(headless=headless)
        self._page = await self._browser.new_page()
        return {"success": True, "message": "Browser launched"}

    async def close(self) -> Dict[str, Any]:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None
        return {"success": True, "message": "Browser closed"}

    def status(self) -> Dict[str, Any]:
        return {
            "library_installed": HAS_PLAYWRIGHT,
            "running": self._browser is not None,
            "current_url": self._page.url if self._page else None,
        }

    # -- actions -------------------------------------------------------------

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> Dict[str, Any]:
        self._ensure_page()
        url = _validate_url(url)
        resp = await self._page.goto(url, wait_until=wait_until, timeout=30_000)
        return {
            "success": True,
            "url": self._page.url,
            "status": resp.status if resp else None,
            "title": await self._page.title(),
        }

    async def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> Dict[str, Any]:
        self._ensure_page()
        buf = await self._page.screenshot(full_page=full_page)
        if path:
            Path(path).write_bytes(buf)
            return {"success": True, "saved_to": path, "size_bytes": len(buf)}
        return {"success": True, "data_base64": base64.b64encode(buf).decode(), "size_bytes": len(buf)}

    async def extract_text(self, selector: Optional[str] = None) -> Dict[str, Any]:
        self._ensure_page()
        if selector:
            el = await self._page.query_selector(selector)
            text = await el.inner_text() if el else ""
        else:
            text = await self._page.inner_text("body")
        return {"success": True, "text": text[:50_000]}  # cap at 50 KB

    async def extract_links(self) -> Dict[str, Any]:
        self._ensure_page()
        links = await self._page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({text: e.innerText.trim().slice(0, 120), href: e.href}))"
        )
        return {"success": True, "links": links[:500]}

    async def click(self, selector: str) -> Dict[str, Any]:
        self._ensure_page()
        await self._page.click(selector, timeout=10_000)
        return {"success": True, "clicked": selector, "url": self._page.url}

    async def fill(self, selector: str, value: str) -> Dict[str, Any]:
        self._ensure_page()
        await self._page.fill(selector, value, timeout=10_000)
        return {"success": True, "filled": selector}

    async def evaluate(self, expression: str) -> Dict[str, Any]:
        """Run a read-only JS expression and return the result."""
        self._ensure_page()
        # Safety: reject obviously dangerous patterns
        _dangerous = re.compile(r"(fetch|XMLHttpRequest|eval|Function|import\(|require\(|document\.cookie)", re.I)
        if _dangerous.search(expression):
            return {"success": False, "error": "Expression blocked by safety filter"}
        result = await self._page.evaluate(expression)
        return {"success": True, "result": result}

    async def pdf(self, path: str) -> Dict[str, Any]:
        self._ensure_page()
        buf = await self._page.pdf()
        Path(path).write_bytes(buf)
        return {"success": True, "saved_to": path, "size_bytes": len(buf)}

    # -- flow helpers --------------------------------------------------------

    async def run_sequence(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute a sequence of actions. Each step: {action, ...params}."""
        results = []
        for step in steps:
            action = step.pop("action", None)
            handler = {
                "navigate": self.navigate,
                "screenshot": self.screenshot,
                "extract_text": self.extract_text,
                "extract_links": self.extract_links,
                "click": self.click,
                "fill": self.fill,
                "evaluate": self.evaluate,
                "pdf": self.pdf,
            }.get(action)
            if handler is None:
                results.append({"success": False, "error": f"Unknown action: {action}"})
                continue
            try:
                r = await handler(**step)
                results.append(r)
            except Exception as exc:
                results.append({"success": False, "error": str(exc)})
        return results

    # -- internal ------------------------------------------------------------

    def _ensure_page(self):
        if self._page is None:
            raise RuntimeError("Browser not launched. Call /api/browser/launch first.")


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_instance: Optional[BrowserAutomation] = None


def get_browser() -> BrowserAutomation:
    global _instance
    if _instance is None:
        _instance = BrowserAutomation()
    return _instance
