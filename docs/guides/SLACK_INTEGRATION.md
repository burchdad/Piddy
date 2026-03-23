# Connect Piddy to Slack - Complete Setup Guide

## Overview

Piddy can now listen to Slack messages in real-time and respond interactively. This guide walks you through setting up the Slack integration completely.

## Prerequisites

- Workspace admin access to your Slack workspace
- Piddy application running (see QUICKSTART.md)
- ANTHROPIC_API_KEY configured

## Step-by-Step Setup

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **"Create New App"**
3. Select **"From scratch"**
4. Enter:
   - **App name**: `Piddy`
   - **Development Slack Workspace**: Choose your workspace
5. Click **"Create App"**

### Step 2: Enable Socket Mode

Socket Mode allows Piddy to receive events in real-time without webhooks.

1. In your app settings, click **"Socket Mode"** (left sidebar)
2. Toggle **"Enable Socket Mode"** to ON
3. Enter a name for your token (e.g., "Piddy Token")
4. Click **"Generate"** to create an **App-Level Token**
5. The token will start with `xapp-`
6. **Copy this token** - you'll need it in `.env`

### Step 3: Configure Event Subscriptions

1. Click **"Event Subscriptions"** (left sidebar)
2. Toggle **"Enable Events"** to ON
3. Under **"Subscribe to bot events"**, click **"Add Bot User Event"**
4. Subscribe to these events:
   - `message.im` — Direct messages to bot
   - `app_mention` — When bot is mentioned in channels
   - `message.channels` — Messages in public channels (optional)
   - `message.groups` — Messages in private channels (optional)
5. Click **"Save Changes"**

### Step 4: Configure OAuth Permissions

1. Click **"OAuth & Permissions"** (left sidebar)
2. Scroll to **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add these scopes:
   - `chat:write` — Send messages
   - `reactions:write` — Add reactions (emoji responses)
   - `commands` — Slash command support
   - `im:read` — Read direct messages
   - `channels:read` — Read channel info
   - `app_mentions:read` — Read mentions

4. Scroll up to **"OAuth Tokens for Your Workspace"**
5. Click **"Reinstall to Workspace"** (to update with new scopes)
6. Click **"Allow"**
7. **Copy the Bot Token** (starts with `xoxb-`)

### Step 5: Configure Slash Commands (Optional)

Slash commands let you trigger specific actions. To add them:

1. Click **"Slash Commands"** (left sidebar)
2. Click **"Create New Command"**
3. Create commands like:

#### Command 1: Review Code
   - **Command**: `/piddy-review`
   - **Request URL**: `http://your-piddy-domain.com/slack/commands/review`
   - **Short Description**: `Review code for quality and security`
   - **Usage hint**: `[code description]`

#### Command 2: Generate Code
   - **Command**: `/piddy-generate`
   - **Request URL**: `http://your-piddy-domain.com/slack/commands/generate`
   - **Short Description**: `Generate backend code`
   - **Usage hint**: `[description]`

#### Command 3: Design Database
   - **Command**: `/piddy-db`
   - **Request URL**: `http://your-piddy-domain.com/slack/commands/db`
   - **Short Description**: `Design database schema`
   - **Usage hint**: `[entities and relationships]`

### Step 6: Configure Environment

Add your tokens to `.env`:

```env
# From Socket Mode (Step 2)
SLACK_APP_TOKEN=xapp-1-...

# From OAuth (Step 4)
SLACK_BOT_TOKEN=xoxb-...

# Also needed
SLACK_SIGNING_SECRET=... (from "Basic Information" page)

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...
```

To find your **Signing Secret**:
1. Go to **"Basic Information"** (left sidebar)
2. Scroll to **"App Credentials"**
3. Copy the **"Signing Secret"**

### Step 7: Install App to Workspace

1. Click **"Install App"** (top of left sidebar)
2. Click **"Install to Workspace"** button
3. Review permissions
4. Click **"Allow"**
5. Copy the **Bot Token** if not already done

### Step 8: Invite Bot to Channels

For Piddy to respond in channels, it needs to be invited:

1. Go to any Slack channel
2. Type: `@Piddy`
3. Slack will prompt to add the app to the channel
4. Click **"Add to channel"** or **"Add this app"**
5. Repeat for other channels where you want Piddy active

## Start Piddy

Now start Piddy with Slack integration enabled:

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start Piddy
python -m src.main
```

You should see:
```
✅ Connected to Slack Socket Mode
✅ Slack Socket Mode listener started
```

## Test the Connection

### In Slack:

1. **Direct Message**: Open a DM with @Piddy and type:
   ```
   Generate a FastAPI endpoint for user registration
   ```

2. **Channel Mention**: In any channel where Piddy is added:
   ```
   @Piddy Design a database schema for a blog
   ```

3. **Slash Command**: Try:
   ```
   /piddy-generate Generate a Python function that validates email
   ```

You should see:
- 🔄 Piddy is thinking (processing emoji)
- Response with code or suggestions
- ✅ Completion indicator

## Using Piddy in Slack

### Message Commands

Just mention Piddy or send a DM with your request:

```
@Piddy Generate a Django REST endpoint for creating users
```

Piddy will automatically detect what you're asking for based on keywords:

| Keyword | Command Type |
|---------|---|
| generate, create, write, code | Code Generation |
| review, analyze, check, audit | Code Review |
| design, schema, database, model | Database Design |
| debug, fix, error, issue | Debugging |
| secure, security, vulnerability | Security Analysis |
| docker, kubernetes, infra, deploy | Infrastructure |
| document, docs, comment | Documentation |
| migrate, migration | Database Migration |

### Response Format

Piddy responds with:
- ✅ or ❌ status indicator
- Formatted code blocks
- Execution time
- Command type used

### Threading

All responses automatically use Slack threads to keep conversations organized and on-topic.

## Emoji Reactions

Piddy uses emoji reactions to show status:
- 🤔 - Processing your request
- ✅ - Completed successfully
- ❌ - Error occurred

## Advanced Usage

### Code with Context

Provide code for analysis:

```
@Piddy Review this code for security issues:

def get_user(user_id):
    from datetime import datetime
    return db.query(User).filter(User.id == user_id).first()
```

### Multi-line Messages

For complex requests, use code blocks:

```
@Piddy I need help with this:

```python
# Existing code
def process_payment(amount, card_token):
    # TODO: Add validation
    return payment_service.charge(amount, card_token)
```

Please add proper error handling and validation.
```

### Following Up

Continue the thread to refine requests:

```
Thread: @Piddy can you also add unit tests?
```

Piddy will refine the previous response.

## Troubleshooting

### Issue: "Piddy not responding"

**Check:**
1. ✅ `.env` has `SLACK_APP_TOKEN` and `SLACK_BOT_TOKEN`
2. ✅ Piddy application is running (`http://localhost:8000/docs` loads)
3. ✅ Piddy is invited to the channel
4. ✅ Check logs for errors

**Solution:**
```bash
# Restart Piddy
python -m src.main
```

### Issue: "Connection refused" errors

**Causes:**
- Piddy isn't running
- Wrong domain/port configuration
- Firewall blocking connections

**Solution:**
1. Ensure Piddy is running locally
2. For Slack commands, use ngrok for tunneling:
   ```bash
   ngrok http 8000
   ```
   Then use the ngrok URL in Slack commands

### Issue: "Socket Mode connection failed"

**Check:**
1. ✅ `SLACK_APP_TOKEN` is correct
2. ✅ Socket Mode is enabled in app settings
3. ✅ Token has `connections:write` scope

**Solution:**
1. Generate a new app-level token
2. Update `.env`
3. Restart Piddy

### Issue: "Bot not responding to mentions"

**Check:**
1. ✅ Bot is invited to channel (`/invite @Piddy`)
2. ✅ `app_mentions:read` scope is enabled
3. ✅ Event subscriptions include `app_mention`

**Solution:**
1. Re-invite bot to channel
2. Reinstall app to workspace (with new scopes)

### Issue: "Permission denied" errors

**Solution:**
Make sure these OAuth scopes are granted:
- `chat:write`
- `reactions:write`
- `commands`
- `app_mentions:read`
- `im:read`
- `channels:read`

If missing, reinstall the app.

## Running Multiple Instances

If running Piddy on multiple servers, use different Slack apps:

1. Create separate apps for each environment (dev, staging, prod)
2. Use different OAuth tokens in each environment
3. Name them clearly: "Piddy-Dev", "Piddy-Staging", "Piddy-Production"

## Monitoring

### Check Logs

```bash
# View Slack connection logs
python -m src.main 2>&1 | grep -i slack
```

### Check Health

```bash
curl http://localhost:8000/api/v1/agent/health
```

### Count Messages Processed

Piddy logs all processed messages. Check your logs to see:
- Total messages processed
- Success/failure rates
- Average response time
- Command types usage

## Best Practices

### 1. Use Threads
Keep conversations organized by using Slack threads

### 2. Be Specific
More specific requests get better results:
- ✅ "Generate a FastAPI GET endpoint that retrieves user by ID with JWT authentication"
- ❌ "Make an endpoint"

### 3. Provide Context
Include relevant context:
```
@Piddy I'm using FastAPI with SQLAlchemy and PostgreSQL. 
Generate a model for a Product entity with: id, name, 
description, price, stock, and timestamps.
```

### 4. Review Before Using
Always review generated code for your specific needs

### 5. Report Issues
If Piddy makes mistakes:
- Report what went wrong
- Provide context
- Piddy will refine its understanding

## Security Considerations

### 1. Never Share Tokens
- Keep `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` private
- Don't commit them to version control
- Use `.env` and `.env.example`

### 2. Verify Signatures
Piddy verifies all Slack requests using the signing secret

### 3. Rate Limiting
Consider implementing rate limits for production

### 4. Audit Logging
Log all Piddy conversations for compliance/security

### 5. Permissions
Review who can use Piddy in your workspace

## Support

If you encounter issues:

1. **Check Documentation**: See [README.md](README.md) and [API.md](API.md)
2. **View Logs**: Check application logs for error messages
3. **Test API**: Use `http://localhost:8000/docs` to test commands
4. **Verify Setup**: Double-check all tokens and scopes

## Next Steps

1. ✅ Set up Slack app (Steps 1-7 above)
2. ✅ Configure `.env` with tokens
3. ✅ Start Piddy
4. ✅ Invite bot to channels
5. ✅ Start chatting with Piddy!

---

You're all set! Start using Piddy in Slack 🚀
