# Quick Start: Activating OpenAI Fallback

## Current Status
✅ Piddy is running with dual-LLM support ready to activate
- **Primary LLM**: Claude Opus 4.6 (Active)
- **Fallback LLM**: GPT-4o (Ready to activate)

## 3-Step Activation

### Step 1: Get Your OpenAI API Key
1. Go to https://platform.openai.com/api/keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)
4. Store it safely

### Step 2: Add Key to .env
```bash
# Edit /workspaces/Piddy/.env and add:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### Step 3: Restart Server
```bash
pkill -9 -f "python src/main.py"
sleep 1
cd /workspaces/Piddy && PYTHONPATH=/workspaces/Piddy:$PYTHONPATH python src/main.py > /tmp/piddy_server.log 2>&1 &
```

## Verify Activation
```bash
# Check logs
tail -20 /tmp/piddy_server.log

# Should NOT show: "OpenAI API key not configured"
# Should show: Agent initialization without warnings
```

## What Happens Now

### When Claude Token Limit is Reached:
1. Piddy detects token exhaustion error
2. Automatically switches to GPT-4o
3. Retries your command
4. Returns result without stalling
5. Logs show: `"Switching from claude-opus-4-6 to gpt-4o"`

### Example:
```
User: "analyze entire project"
Claude: 60% done, tokens exhausted ❌
Piddy: Switches to GPT-4o ✨
GPT-4o: Completes remaining 40% ✅
User: Gets full analysis (no stalling!)
```

## Testing the Fallback

Send a complex task that uses many tokens:
```
describe the entire architecture, identify all anti-patterns, 
list all duplicate code, propose refactoring, add security analysis
```

If it completes after Claude would have failed, fallback worked!

## Support

- **Issue**: Can't find my OpenAI API key
  - Answer: https://platform.openai.com/api/keys

- **Issue**: Need more tokens?
  - Answer: Add billing to your OpenAI account at https://platform.openai.com/account/billing

- **Issue**: Still stalling?
  - Answer: Check that OPENAI_API_KEY is in .env and server restarted

## Cost Considerations

### Usage Estimates:
- **Claude (Primary)**: ~$0.01 per 1K tokens
- **GPT-4o (Fallback)**: ~$0.015 per 1K tokens
- **Fallback only activates** when Claude fails (not every request)

### Expected Cost:
- Most queries: Claude only (cheaper)
- Long complex tasks causing token exhaustion: Fallback only charges for remaining tokens
- Total cost: Usually lower than GPT-4o would be alone

## That's It!

Your Piddy now has unlimited LLM capacity - no more stalling on long tasks! 🚀
