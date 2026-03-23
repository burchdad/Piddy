# Slack Integration Guide

## Overview

Piddy integrates with Slack to provide real-time backend development assistance to your team. Communication happens through:

- **Direct Messages**: Send tasks directly to Piddy
- **Channel Mentions**: Tag @Piddy in channels for team-wide collaboration
- **Slash Commands**: Use custom commands for specific tasks
- **Message Threads**: Keep discussions organized in threads

## Setting Up Slack Integration

### Step 1: Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name it "Piddy" and select your workspace

### Step 2: Configure Basic Information

1. Go to "Basic Information"
2. Save the following for later:
   - Signing Secret (for webhook verification)
   - App-Level Tokens (generate one with `connections:write` scope)

### Step 3: Enable Socket Mode

1. Go to "Socket Mode" in left sidebar
2. Toggle "Enable Socket Mode"
3. Generate an App-Level Token with `connections:write` scope
4. Save this token

### Step 4: Configure Event Subscriptions

1. Go to "Event Subscriptions"
2. Enable Events
3. Subscribe to bot events:
   - `message.im` - Direct messages to bot
   - `app_mention` - When bot is mentioned
   - `message.channels` - Messages in channels (optional)
   - `message.groups` - Messages in private channels (optional)

### Step 5: Set Up Slash Commands (Optional)

1. Go to "Slash Commands"
2. Create commands like:
   - `/piddy-help` - Get help on available commands
   - `/piddy-status` - Check agent status
   - `/piddy-generate` - Generate code

### Step 6: OAuth & Permissions

1. Go to "OAuth & Permissions"
2. Add OAuth Scopes under "Bot Token Scopes":
   - `chat:write` - Send messages
   - `reactions:write` - Add reactions
   - `chat:write.public` - Post in public channels
   - `chat:write.customize` - Customize messages
   - `app_mentions:read` - Read mentions
   - `im:read` - Read DMs
   - `channels:read` - Read channel info
   - `groups:read` - Read private channel info

### Step 7: Install or Reinstall App

1. Go to "Install App"
2. Reinstall to update scopes
3. Copy the Bot Token (starts with `xoxb-`)

### Step 8: Configure Environment

Update your `.env` file:

```env
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
SLACK_SIGNING_SECRET=xxxxxxxxxxxxxxxxxxxx
SLACK_APP_TOKEN=xapp-1-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
```

## Event Handling

### Message Events

When someone mentions Piddy or sends a direct message:

1. Slack sends an event to Piddy's event endpoint
2. Piddy verifies the request signature
3. Piddy extracts the message text and context
4. Command is sent to the backend developer agent
5. Agent processes and responds

### Threaded Conversations

Messages are automatically kept in threads to maintain context:

- First message starts a new thread
- Agent responses maintain the thread
- Continuous context through thread_ts

## API Integration

The Slack integration exposes these endpoints:

### POST /slack/events

Receives all Slack events (messages, mentions, etc.)

**Headers Required:**
- `X-Slack-Request-Timestamp`: Timestamp of request
- `X-Slack-Signature`: HMAC signature for verification

**Payload Examples:**

URL Verification:
```json
{
  "type": "url_verification",
  "challenge": "3eZbrw1aBcXcDIRpYcDmZYw=="
}
```

Message Event:
```json
{
  "type": "event_callback",
  "event": {
    "type": "message",
    "channel": "C1234567890",
    "user": "U1234567890",
    "text": "@Piddy generate a FastAPI endpoint",
    "ts": "1234567890.000001"
  }
}
```

## Usage Examples

### Direct Message

Send a direct message to @Piddy:

```
Hey Piddy, generate a Python function that validates email addresses
```

### Channel Mention

```
@Piddy I need a database schema for a user management system
```

### With Context

```
@Piddy Generate a FastAPI endpoint for user authentication with:
- JWT token-based auth
- Refresh token support
- Rate limiting
```

## Slash Commands

If configured, use slash commands:

```
/piddy-generate Generate a REST API endpoint for file uploads
```

## Response Format

Piddy responds with well-formatted messages including:

- Summary of the request
- Solution or code generated
- Explanations and best practices
- Links to relevant documentation
- Action items or next steps

## Error Handling

If something goes wrong:

- Piddy will acknowledge the request with a reaction (👀)
- Process the request
- Respond with either the result or detailed error explanation
- Add reactions for status: ✅ (success), ❌ (error)

## Monitoring

Check Piddy's status in Slack:

```
/piddy-status
```

Response includes:
- Agent availability
- Current queue length
- Recent task statistics
- Any errors or issues

## Troubleshooting

### "Request signature verification failed"

- Verify SLACK_SIGNING_SECRET matches Slack app settings
- Check request timestamp (within 5 minutes)

### "Bot not responding to mentions"

- Verify bot has `app_mentions:read` scope
- Check Socket Mode is enabled
- Verify SLACK_BOT_TOKEN is correct

### "Messages not sent back"

- Verify `chat:write` scope is enabled
- Check bot is invited to channel/DM
- Verify message formatting

## Advanced Customization

### Custom Responses

Responses can be customized with:
- Rich formatting (bold, italics, code blocks)
- Attachments (files, images)
- Interactive elements (buttons, select menus)

### Context Preservation

Piddy maintains context across:
- Message threads
- User history (within session)
- Channel context

## Security Considerations

1. **Never share tokens**: Keep SLACK_BOT_TOKEN and SLACK_APP_TOKEN secure
2. **Verify signatures**: Always verify Slack request signatures
3. **Rate limiting**: Implement rate limiting for API endpoints
4. **Sensitive data**: Don't log sensitive information
5. **Scope minimization**: Only request necessary OAuth scopes
