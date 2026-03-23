# Piddy Slack Integration - Troubleshooting & FAQ

## Troubleshooting

### Piddy Doesn't Respond to Mentions

**Symptoms**: You mention @Piddy but get no response or error reaction

**Causes & Solutions**:

1. **Piddy not running**
   ```bash
   # Start Piddy
   python -m src.main
   # Or use the startup script
   bash start-slack.sh  # Linux/Mac
   start-slack.bat     # Windows
   ```

2. **Bot not invited to channel**
   - Go to the channel in Slack
   - Type `@Piddy` and select "Add Piddy to this channel"
   - Or click the channel name → "Members" → "Add people/apps"

3. **Invalid tokens in .env**
   - Verify `SLACK_BOT_TOKEN` starts with `xoxb-`
   - Verify `SLACK_APP_TOKEN` starts with `xapp-1-`
   - Check no quotes or extra spaces in .env file
   - Copy tokens carefully from https://api.slack.com/apps

4. **Socket Mode not enabled**
   - Go to https://api.slack.com/apps
   - Open your Piddy app
   - Click "Socket Mode" in left sidebar
   - Toggle "Enable Socket Mode" ON

5. **Event subscriptions not configured**
   - Go to your Slack app → "Event Subscriptions"
   - Ensure "Enable Events" is ON
   - Check that `app_mention` is checked under "Subscribe to bot events"
   - For DMs, check `message.im` is also checked

### "Connection refused" or Network Error

**Symptoms**: Error about connecting to localhost

**Solutions**:

1. **Piddy port in use**
   ```bash
   # Find what's using port 8000
   lsof -i :8000  # Linux/Mac
   # Or in Windows PowerShell
   netstat -ano | findstr :8000
   
   # Kill the process or use a different port
   export SERVER_PORT=8001  # In .env
   ```

2. **Firewall blocking**
   - Check that localhost:8000 is not blocked
   - Try: `curl http://localhost:8000/`
   - Should return app info in JSON

3. **Piddy crashed**
   - Check the terminal output for error messages
   - Restart: `python -m src.main`
   - Check logs for stack traces

### "Invalid token" Error

**Symptoms**: Auth fails when starting Piddy

**Causes & Solutions**:

1. **Wrong token type**
   - `SLACK_BOT_TOKEN` must start with `xoxb-` (bot token)
   - `SLACK_APP_TOKEN` must start with `xapp-1-` (app token)
   - `SLACK_SIGNING_SECRET` starts with no prefix (webhook secret)
   - Don't mix them up!

2. **Expired token**
   - If token is old, regenerate it
   - Go to https://api.slack.com/apps → your app
   - Copy fresh tokens from the app page

3. **Wrong workspace**
   - Verify you're in the right Slack workspace
   - Check app is installed in that workspace
   - Go to your workspace settings → "Installed Apps"

### Piddy Responds But Commands Fail

**Symptoms**: Piddy acknowledges but says it can't process request

**Causes & Solutions**:

1. **ANTHROPIC_API_KEY missing or invalid**
   ```bash
   # In .env:
   ANTHROPIC_API_KEY=sk-ant-...  # Should start with sk-ant-
   ```
   - Check key is valid at https://console.anthropic.com
   - Ensure no extra quotes or spaces

2. **Rate limit**
   - If using free tier, reduced API limits apply
   - Wait a minute and try again
   - Check Anthropic console for usage

3. **Agent error in logs**
   - Check terminal where Piddy is running
   - Look for error stack traces
   - Share the error in the troubleshooting channel

### Slow Responses from Piddy

**Causes & Solutions**:

1. **Complex request**
   - First responses take 10-30 seconds (normal)
   - Large code generation may take 60+ seconds
   - Wait for ✅ reaction indicating completion

2. **Network latency**
   - Check your internet connection
   - Try a simpler request first
   - Verify `curl http://localhost:8000/api/v1/agent/health` is fast

3. **System overload**
   - Check CPU/memory usage
   - Close other applications
   - Restart Piddy: `python -m src.main`

### "Permission denied" When Running Script

**Windows Symptoms**:
```
start-slack.bat is not recognized
```

**Solutions**:
- Double-click `start-slack.bat` instead of running from command line
- Or use: `cmd /c start-slack.bat`
- Ensure you're in the Piddy directory

**Linux/Mac Symptoms**:
```
Permission denied: start-slack.sh
```

**Solutions**:
```bash
# Make script executable
chmod +x start-slack.sh
# Then run
bash start-slack.sh
```

## FAQ

### How do I get my tokens?

**Step 1: Create Slack App**
- Go to https://api.slack.com/apps
- Click "Create New App" → "From scratch"
- Name: "Piddy", Workspace: yours
- Click "Create App"

**Step 2: Get SLACK_BOT_TOKEN (xoxb)**
- Click "OAuth & Permissions" in left menu
- Scroll to "Bot Token Scopes"
- Add scopes:
  - `chat:write`
  - `reactions:write`
  - `app_mentions:read`
  - `im:history` (optional for DM history)
- Scroll to "OAuth Tokens for Your Workspace"
- Click "Install to Workspace"
- Copy the "Bot User OAuth Token" (starts with `xoxb-`)
- Paste as `SLACK_BOT_TOKEN` in `.env`

**Step 3: Get SLACK_APP_TOKEN (xapp)**
- Click "Socket Mode" in left menu
- Toggle "Enable Socket Mode" ON
- Click "Generate an app-level token"
- Name it "Socket"
- Grant `connections:write` scope
- Copy the token (starts with `xapp-1-`)
- Paste as `SLACK_APP_TOKEN` in `.env`

**Step 4: Get SLACK_SIGNING_SECRET**
- Click "Basic Information" in left menu
- Find "Signing Secret" section
- Copy the secret (no prefix)
- Paste as `SLACK_SIGNING_SECRET` in `.env`

**Step 5: Get ANTHROPIC_API_KEY**
- Go to https://console.anthropic.com/account/keys
- Click "Create Key"
- Copy the key (starts with `sk-ant-`)
- Paste as `ANTHROPIC_API_KEY` in `.env`

### Can I run Piddy on a server/cloud?

**Yes!** But you need:

1. **Public IP/Domain**
   - Slack needs to reach your server
   - If using Socket Mode (current setup), you don't need webhooks
   - Current setup works fine behind firewalls

2. **Environment variables**
   - Same tokens work on any server
   - Set `SERVER_HOST=0.0.0.0` in `.env`
   - Set `SERVER_PORT=8000` (or any available port)

3. **Docker**
   ```bash
   docker build -t piddy .
   docker run -p 8000:8000 --env-file .env piddy
   ```

4. **Docker Compose**
   ```bash
   docker-compose up -d
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full cloud deployment guide.

### How do I use Piddy with other AI agents?

Other agents can call Piddy's API:

```bash
curl -X POST "http://piddy-server:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "code_generation",
    "description": "Generate a FastAPI endpoint",
    "priority": 8
  }'
```

See [API.md](API.md) for complete API reference.

### What if I want to run multiple instances?

**Option 1: Different Slack apps per instance**
- Create separate Slack apps for dev/staging/production
- Got to https://api.slack.com/apps
- Click "Create New App" for each
- Each gets its own tokens
- Set in `.env` files

**Option 2: Load balancing**
- Put multiple instances behind a load balancer
- All use same Slack tokens
- Need shared state (e.g., Redis) for message coordination
- See [DEPLOYMENT.md](DEPLOYMENT.md) for details

### Can I customize the keyword detection?

**Current implementation**: Keywords map to command types
- `generate/create/write` → Code generation
- `review/analyze/check` → Code review
- `design/schema/database` → Database design
- `docker/kubernetes/infra` → Infrastructure

**To customize**:
1. Edit [src/integrations/slack_handler.py](src/integrations/slack_handler.py)
2. Find `_parse_message_to_command()` method
3. Add/modify keyword patterns:
   ```python
   if "your-keyword" in text:
       command_type = CommandType.YOUR_COMMAND_TYPE
   ```
4. Restart Piddy

**Better option**: Use LLM-based intent detection (coming soon)

### How do I add slash commands?

**Option 1: Manual - Add in Slack App**
1. Go to https://api.slack.com/apps → your app
2. Click "Slash Commands" in left menu
3. Click "Create New Command"
4. Command: `/piddy-generate`
5. Request URL: `http://your-server:8000/slack/slash`
6. Description: "Generate backend code"

**Option 2: Piddy will handle it automatically**
- Slash commands are already configured in Socket Mode
- Just run the script with slash commands enabled
- See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) for details

### Can Piddy learn from messages?

**Not yet.** Current features:
- ✅ Responds to each message independently
- ✅ Maintains conversation context in threads
- ⏳ Message history persistence (planned)
- ⏳ Learning from past interactions (planned)

### What models does Piddy use?

**Default**: Claude 3 Opus (most capable)

**Available**:
- `claude-3-opus-20240229` (default, best for complex tasks)
- `claude-3-sonnet-20240229` (faster, cheaper)
- `claude-3-haiku-20240307` (fastest, most limited)

**Change in `.env`**:
```env
AGENT_MODEL=claude-3-sonnet-20240229
```

See [CAPABILITIES.md](CAPABILITIES.md) for model comparison.

### Can I use different AI providers?

**Currently**: Only Anthropic (Claude models)

**Roadmap**: OpenAI, Google (Gemini), Cohere support planned

**To extend** (advanced):
- Edit [src/agent/core.py](src/agent/core.py)
- Modify LLM initialization
- Implement your own LLM adapter

### How do I run tests?

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run specific file
pytest tests/test_agent.py

# Run with coverage
pytest --cov=src tests/
```

### How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Pull request process
- Adding new tools
- Testing requirements

### Where do I report bugs?

1. **Check if it's already reported**: Search issues
2. **Create new issue** with:
   - What you tried
   - What happened
   - Error message/logs
   - Your setup (OS, Python version, etc.)

### Can I use Piddy for production?

**Current Status**: MVP (Minimum Viable Product)

**Production ready for**:
- ✅ Code generation and templates
- ✅ Code review and analysis
- ✅ Slack integration basics

**Not yet production ready**:
- ❌ High-traffic scenarios (add caching/queuing)
- ❌ Complex concurrent operations (add job queue)
- ❌ Long-term reliability (add monitoring/alerting)
- ❌ Sensitive data (add encryption/audit logs)

**To prepare for production**:
See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Docker/Kubernetes setup
- Environment configuration
- Security hardening
- Monitoring & logging
- High availability setup

## Getting Help

1. **Check this guide**: Most issues covered above
2. **Check SLACK_INTEGRATION.md**: Setup issues
3. **Check QUICKSTART.md**: Basic usage
4. **Check API.md**: Advanced API features
5. **Create an issue**: With full error details
6. **Email support**: Your organization's support channel

## Performance Tips

### Speed up responses

1. **Use warmed-up instance**
   - First request is slower (model loading)
   - Subsequent requests are faster

2. **Use simpler models for quick tasks**
   ```env
   AGENT_MODEL=claude-3-haiku-20240307
   ```

3. **Provide better context**
   ```
   @Piddy I'm using FastAPI with PostgreSQL.
   Generate a user model with: id, email, name, created_at
   ```

4. **Use batch processing**
   - Multiple requests at once via API
   - See [API.md](API.md) for batch endpoint

### Reduce costs

1. **Use cheaper models** (if accuracy acceptable)
   ```env
   AGENT_MODEL=claude-3-sonnet-20240229
   ```

2. **Set max tokens**
   ```env
   AGENT_MAX_TOKENS=2048  # Lower = cheaper
   ```

3. **Cache responses**
   - Don't ask same question twice
   - Save generated code

---

**Still stuck?** Create an issue or contact your team lead!
