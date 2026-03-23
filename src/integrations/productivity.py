"""
Productivity connectors for Piddy.

Google Calendar, Jira, and Notion integrations.
All connectors require API tokens configured in settings / key_manager.
Network calls are wrapped in try/except so offline mode degrades gracefully.
"""

import logging
import json
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared HTTP helper (no extra dependencies beyond stdlib)
# ---------------------------------------------------------------------------
import urllib.request
import urllib.error


def _api_call(
    url: str,
    *,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    """Minimal HTTP helper using only stdlib."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"status": resp.status, "data": json.loads(resp.read())}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "error": exc.reason}
    except Exception as exc:
        return {"status": 0, "error": str(exc)}


# ============================================================================
# Google Calendar
# ============================================================================
class GoogleCalendarConnector:
    """Read-only Google Calendar integration via API key + calendar ID.

    For full OAuth write access, users should configure a service account.
    This lightweight version uses the public calendar API endpoint.
    """

    BASE = "https://www.googleapis.com/calendar/v3"

    def __init__(self, api_key: str = "", calendar_id: str = "primary"):
        self.api_key = api_key
        self.calendar_id = calendar_id

    def configured(self) -> bool:
        return bool(self.api_key)

    def list_events(self, days_ahead: int = 7, max_results: int = 20) -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Google Calendar API key not configured"}
        now = datetime.utcnow().isoformat() + "Z"
        end = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"
        url = (
            f"{self.BASE}/calendars/{self.calendar_id}/events"
            f"?key={self.api_key}&timeMin={now}&timeMax={end}"
            f"&maxResults={max_results}&singleEvents=true&orderBy=startTime"
        )
        resp = _api_call(url)
        if "error" in resp:
            return resp
        items = resp.get("data", {}).get("items", [])
        return {
            "count": len(items),
            "events": [
                {
                    "summary": e.get("summary", "(no title)"),
                    "start": (e.get("start") or {}).get("dateTime") or (e.get("start") or {}).get("date"),
                    "end": (e.get("end") or {}).get("dateTime") or (e.get("end") or {}).get("date"),
                    "location": e.get("location"),
                    "link": e.get("htmlLink"),
                }
                for e in items
            ],
        }

    def status(self) -> Dict[str, Any]:
        return {"connector": "google_calendar", "configured": self.configured()}


# ============================================================================
# Jira
# ============================================================================
class JiraConnector:
    """Jira Cloud REST API v3 connector (Basic Auth via API token)."""

    def __init__(self, base_url: str = "", email: str = "", api_token: str = ""):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token

    def configured(self) -> bool:
        return bool(self.base_url and self.email and self.api_token)

    def _headers(self) -> Dict[str, str]:
        import base64
        cred = base64.b64encode(f"{self.email}:{self.api_token}".encode()).decode()
        return {"Authorization": f"Basic {cred}", "Accept": "application/json"}

    def search_issues(self, jql: str = "assignee=currentUser() ORDER BY updated DESC", max_results: int = 20) -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Jira not configured (base_url, email, api_token required)"}
        url = f"{self.base_url}/rest/api/3/search?jql={urllib.parse.quote(jql)}&maxResults={max_results}"
        resp = _api_call(url, headers=self._headers())
        if "error" in resp:
            return resp
        issues = resp.get("data", {}).get("issues", [])
        return {
            "count": len(issues),
            "issues": [
                {
                    "key": i["key"],
                    "summary": i["fields"].get("summary"),
                    "status": (i["fields"].get("status") or {}).get("name"),
                    "assignee": (i["fields"].get("assignee") or {}).get("displayName"),
                    "priority": (i["fields"].get("priority") or {}).get("name"),
                    "updated": i["fields"].get("updated"),
                }
                for i in issues
            ],
        }

    def create_issue(self, project_key: str, summary: str, description: str = "", issue_type: str = "Task") -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Jira not configured"}
        url = f"{self.base_url}/rest/api/3/issue"
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description or summary}]}],
                },
                "issuetype": {"name": issue_type},
            }
        }
        resp = _api_call(url, method="POST", headers=self._headers(), body=payload)
        if "error" in resp:
            return resp
        data = resp.get("data", {})
        return {"success": True, "key": data.get("key"), "id": data.get("id"), "self": data.get("self")}

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Jira not configured"}
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        resp = _api_call(url, headers=self._headers())
        if "error" in resp:
            return resp
        return resp.get("data", {})

    def status(self) -> Dict[str, Any]:
        return {"connector": "jira", "configured": self.configured(), "base_url": self.base_url}


# ============================================================================
# Notion
# ============================================================================
class NotionConnector:
    """Notion API connector (v2022-06-28)."""

    BASE = "https://api.notion.com/v1"

    def __init__(self, api_token: str = ""):
        self.api_token = api_token

    def configured(self) -> bool:
        return bool(self.api_token)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Notion-Version": "2022-06-28",
        }

    def search(self, query: str = "", page_size: int = 20) -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Notion API token not configured"}
        url = f"{self.BASE}/search"
        body: Dict[str, Any] = {"page_size": page_size}
        if query:
            body["query"] = query
        resp = _api_call(url, method="POST", headers=self._headers(), body=body)
        if "error" in resp:
            return resp
        results = resp.get("data", {}).get("results", [])
        return {
            "count": len(results),
            "pages": [
                {
                    "id": r.get("id"),
                    "type": r.get("object"),
                    "title": _notion_title(r),
                    "url": r.get("url"),
                    "last_edited": r.get("last_edited_time"),
                }
                for r in results
            ],
        }

    def create_page(self, parent_id: str, title: str, content: str = "") -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Notion API token not configured"}
        url = f"{self.BASE}/pages"
        body = {
            "parent": {"database_id": parent_id},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]},
            },
        }
        if content:
            body["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]},
                }
            ]
        resp = _api_call(url, method="POST", headers=self._headers(), body=body)
        if "error" in resp:
            return resp
        data = resp.get("data", {})
        return {"success": True, "id": data.get("id"), "url": data.get("url")}

    def get_page(self, page_id: str) -> Dict[str, Any]:
        if not self.configured():
            return {"error": "Notion API token not configured"}
        url = f"{self.BASE}/pages/{page_id}"
        resp = _api_call(url, headers=self._headers())
        if "error" in resp:
            return resp
        return resp.get("data", {})

    def status(self) -> Dict[str, Any]:
        return {"connector": "notion", "configured": self.configured()}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _notion_title(result: Dict) -> str:
    """Extract title string from a Notion search result."""
    props = result.get("properties", {})
    for v in props.values():
        if v.get("type") == "title":
            parts = v.get("title", [])
            return "".join(p.get("plain_text", "") for p in parts)
    return "(untitled)"


# ---------------------------------------------------------------------------
# Aggregated status for all connectors
# ---------------------------------------------------------------------------
def get_all_connector_status() -> Dict[str, Any]:
    from config.settings import get_settings
    s = get_settings()

    cal = GoogleCalendarConnector(
        api_key=getattr(s, "google_calendar_api_key", ""),
        calendar_id=getattr(s, "google_calendar_id", "primary"),
    )
    jira = JiraConnector(
        base_url=getattr(s, "jira_base_url", ""),
        email=getattr(s, "jira_email", ""),
        api_token=getattr(s, "jira_api_token", ""),
    )
    notion = NotionConnector(api_token=getattr(s, "notion_api_token", ""))

    return {
        "google_calendar": cal.status(),
        "jira": jira.status(),
        "notion": notion.status(),
    }
