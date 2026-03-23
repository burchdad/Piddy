---
name: automation-workflows
description: Design and build automation workflows with triggers, actions, and integrations across tools like Zapier, Make, n8n, and custom scripts
---

# Automation Workflows

Design and implement automation workflows to eliminate repetitive tasks and connect tools together.

## Automation Opportunity Identification

### Signs you need automation

```
□ You do the same task 3+ times per week
□ The task follows a predictable pattern
□ It involves copying data between tools
□ It's triggered by a specific event
□ Errors happen when done manually
□ It takes significant time but little thought
```

### High-value automation targets

| Task | Trigger | Automation |
|------|---------|------------|
| Deploy on merge | PR merged to main | CI/CD pipeline |
| Notify team of errors | Error rate spike | Alert → Slack/email |
| Back up database | Daily at 2am | Cron job |
| Update docs | Code change | Auto-generate from source |
| Create Jira ticket from bug | Bug report filed | Webhook → ticket |
| Sync contacts | New signup | CRM integration |

## Workflow Design Pattern

```
TRIGGER → CONDITION → ACTION → RESULT

Example:
  New GitHub issue created
    → IF label == "bug" AND priority == "high"
    → THEN create Slack message in #critical-bugs
    → AND assign to on-call developer
```

### Workflow Components

1. **Trigger**: What starts the workflow (event, schedule, manual)
2. **Filter/Condition**: Should it proceed? (if/else logic)
3. **Action**: What to do (API call, notification, file operation)
4. **Error Handling**: What if an action fails? (retry, fallback, alert)
5. **Logging**: Record what happened for debugging

## Platform Comparison

| Feature | Zapier | Make (Integromat) | n8n | Custom Script |
|---------|--------|-------------------|-----|---------------|
| Ease of use | Easiest | Medium | Medium | Hardest |
| Cost | $$ | $ | Free (self-host) | Free |
| Flexibility | Limited | Good | Excellent | Unlimited |
| Integrations | 5000+ | 1000+ | 400+ | Any API |
| Self-hosted | No | No | Yes | Yes |
| Best for | Simple 2-step | Complex multi-step | Technical users | Total control |

## Custom Automation with Python

### Webhook Receiver

```python
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/webhooks/github")
async def github_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    if event == "issues" and payload["action"] == "opened":
        issue = payload["issue"]
        if "bug" in [l["name"] for l in issue["labels"]]:
            await notify_slack(
                channel="#bugs",
                text=f"New bug: {issue['title']}\n{issue['html_url']}"
            )
    return {"status": "ok"}
```

### Scheduled Tasks

```python
import schedule
import time

def daily_backup():
    # Run database backup
    ...

def hourly_health_check():
    # Check all services are up
    ...

schedule.every().day.at("02:00").do(daily_backup)
schedule.every().hour.do(hourly_health_check)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### File Watcher

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Changed: {event.src_path}")
            run_tests()
            run_linter()

observer = Observer()
observer.schedule(CodeChangeHandler(), path='src/', recursive=True)
observer.start()
```

## Workflow Patterns

### Fan-out / Fan-in

```
Trigger
  ├── Action A (parallel)
  ├── Action B (parallel)
  └── Action C (parallel)
      └── Wait for all → Final action
```

### Sequential Pipeline

```
Step 1 → Step 2 → Step 3 → Step 4
(each step uses output from the previous)
```

### Retry with Backoff

```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait)
```

## Testing Automations

1. **Dry run** — Log what WOULD happen without actually doing it
2. **Single item** — Test with one record before batch
3. **Error path** — Deliberately trigger failures to test error handling
4. **Rate limits** — Verify you won't hit API rate limits at scale
5. **Idempotency** — Running the same automation twice shouldn't duplicate results
