---
name: browser-automation
description: Automate browsers with Playwright — navigation, selectors, screenshots, scraping, and end-to-end testing
---

# Browser Automation with Playwright

## Setup

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

## Async Usage

```python
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        print(await page.title())
        await browser.close()
```

## Navigation and Waiting

```python
page.goto("https://example.com", wait_until="networkidle")
page.wait_for_selector("#content")
page.wait_for_load_state("domcontentloaded")
page.wait_for_url("**/dashboard")
page.wait_for_timeout(1000)  # last resort
```

## Selectors and Interaction

```python
# Click, fill, type
page.click("button#submit")
page.fill("input[name='email']", "user@example.com")
page.type("#search", "query", delay=100)  # simulates typing

# Select, check
page.select_option("select#country", "US")
page.check("input#agree")

# Text-based selectors
page.click("text=Sign In")
page.click("role=button[name='Submit']")

# Get text / attributes
text = page.text_content(".result")
href = page.get_attribute("a.link", "href")
```

## Screenshots and PDF

```python
page.screenshot(path="screenshot.png", full_page=True)
page.pdf(path="page.pdf", format="A4")

# Element screenshot
page.locator("#chart").screenshot(path="chart.png")
```

## Scraping Patterns

```python
# Get all links
links = page.eval_on_selector_all("a", "els => els.map(e => e.href)")

# Table data
rows = page.locator("table tbody tr")
for i in range(rows.count()):
    cells = rows.nth(i).locator("td")
    row_data = [cells.nth(j).text_content() for j in range(cells.count())]

# Intercept network responses
page.on("response", lambda r: print(r.url) if "api" in r.url else None)
```

## Authentication

```python
# Save and reuse auth state
context = browser.new_context(storage_state="auth.json")
# After login:
context.storage_state(path="auth.json")
```

## Key Patterns
- Always use `headless=True` for CI/automation, `headless=False` for debugging
- Prefer `page.locator()` over `page.query_selector()` — auto-waits
- Use `expect(locator).to_be_visible()` for assertions in tests
- Network interception: `page.route("**/api/**", handler)` for mocking
- Multiple pages: `context.new_page()` for tabs
- File upload: `page.set_input_files("input[type=file]", "path/to/file")`
- Downloads: `page.expect_download()` context manager
- Mobile emulation: `browser.new_context(viewport={"width": 375, "height": 667})`
