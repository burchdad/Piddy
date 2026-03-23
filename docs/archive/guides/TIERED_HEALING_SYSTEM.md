# Tiered Self-Healing System: Local → Claude → OpenAI

## Overview

Piddy now has a **three-tier self-healing system** that uses intelligent fallback logic:

```
Start → Tier 1: Local Patterns
              ↓ (if fails/no match)
           Tier 2: Claude Analysis
              ↓ (if tokens run out)
           Tier 3: OpenAI Final Fallback
              ↓
           Done!
```

## Tier 1: Local Pattern Healing (FREE)

**Cost**: Zero external API calls  
**Speed**: Instant (pattern matching only)  
**Available**: Always (no tokens to track)

### What It Does
- ✅ Converts `print()` to `logger.info()`
- ✅ Fixes broad exception handlers
- ✅ Removes mock data automatically
- ✅ Converts hardcoded values to config
- ✅ Auto-detects and adds missing imports

### Use Cases
- Simple code quality fixes
- Mock data removal
- Import cleanup
- Offline environments

**Use it directly:**
```bash
curl -X POST http://localhost:8000/api/self/fix-all-local
```

---

## Tier 2: Claude Analysis (WITH TOKEN TRACKING)

**Cost**: Anthropic API tokens (tracked)  
**Speed**: 2-5 seconds per analysis  
**Available**: When you have Claude API key

### What It Does
- 🔵 Deep code analysis
- 🔵 Complex issue solving
- 🔵 Architectural recommendations
- 🔵 Context-aware fixes

### Token Tracking

Each session has limits:
- **Claude limit**: 1,000,000 tokens per session
- **OpenAI limit**: 500,000 tokens per session

Check current usage:
```bash
curl http://localhost:8000/api/self/status
```

Response includes:
```json
{
  "token_usage": {
    "claude": {
      "used": 45230,
      "limit": 1000000,
      "remaining": 954770
    },
    "openai": {
      "used": 0,
      "limit": 500000
    }
  }
}
```

### Use Cases
- Complex architectural changes
- When local patterns don't match
- Deep code analysis needs
- "I need Claude to look at this"

**Force Claude only:**
```bash
curl -X POST http://localhost:8000/api/self/fix-claude
```

---

## Tier 3: OpenAI Final Fallback

**Cost**: OpenAI API tokens (tracked)  
**Speed**: 3-8 seconds per analysis  
**Available**: When Claude tokens exhausted

### What It Does
- 🟢 GPT-4o level analysis
- 🟢 All issues Claude couldn't solve
- 🟢 Most comprehensive fixes
- ⚠️ Highest cost tier (use when needed)

### When to Use
- Claude ran out of tokens
- Emergency situation
- Need guaranteed resolution
- Complex multi-file refactoring

**Force OpenAI only (last resort):**
```bash
curl -X POST http://localhost:8000/api/self/fix-openai
```

---

## The Smart Fallback Flow

### Automatic Tiered Healing

```bash
curl -X POST http://localhost:8000/api/self/fix-all
```

**What happens:**
1. Tries **Tier 1** (Local patterns) → If successful, DONE ✅
2. If Tier 1 can't handle it:
   - Tries **Tier 2** (Claude) → If successful, DONE ✅
   - If Claude available and tokens allow
3. If Claude runs out or unavailable:
   - Tries **Tier 3** (OpenAI) → Always completes ✅

**Response shows which tier was used:**
```json
{
  "status": "self-fix_complete",
  "tier_used": 1,
  "engine": "local_self_healing",
  "uses_external_ai": false,
  "ai_cost": "FREE",
  "token_status": {
    "claude": { "used": 0, "remaining": 1000000 },
    "openai": { "used": 0, "remaining": 500000 }
  }
}
```

---

## API Endpoints

### 1. Auto-Fix (Smart Tiering)
```bash
POST /api/self/fix-all
```
**Response**: Uses Tier 1 → 2 → 3 automatically based on availability

### 2. Force Tier 1 (Local Only)
```bash
POST /api/self/fix-all-local
```
**Response**: Local pattern matching only, no AI

### 3. Force Tier 2 (Claude)
```bash
POST /api/self/fix-claude
```
**Response**: Claude analysis, tracks tokens

### 4. Force Tier 3 (OpenAI)
```bash
POST /api/self/fix-openai
```
**Response**: GPT-4o analysis, tracks tokens

### 5. Check Status
```bash
GET /api/self/status
```
**Response**: Token usage, tier availability, all endpoints

### 6. Run Audit
```bash
POST /api/self/audit
```
**Response**: System health check before healing

### 7. Go Live
```bash
POST /api/self/go-live
```
**Response**: Complete sequence: audit → fix → PR creation

---

## Configuration

### Add API Keys

Create `.env` file in project root:

```bash
# For Tier 2 (Claude)
ANTHROPIC_API_KEY=sk-ant-xxx...

# For Tier 3 (OpenAI)
OPENAI_API_KEY=sk-xxx...
```

Or on Railway/Vercel, add as environment variables.

### Adjust Token Limits

Edit `src/tiered_healing_engine.py`:

```python
class TokenTracker:
    def __init__(self):
        self.claude_session_limit = 1000000  # Adjust here
        self.openai_session_limit = 500000   # Adjust here
```

---

## Usage Examples

### Example 1: Simple Fix (Tier 1)

```bash
curl -X POST http://localhost:8000/api/self/fix-all
```

**Likely outcome**: ✅ Tier 1 (Local) handles it in milliseconds
- Mock data removed
- Print statements converted to logging
- Missing imports added
- **Cost**: ZERO

---

### Example 2: Complex Issue (Tier 2)

```bash
curl -X POST http://localhost:8000/api/self/fix-all
```

**When this happens**:
- Local patterns don't match the issue
- System automatically escalates to Claude
- Claude analyzes code context
- **Cost**: ~5K-50K tokens

**Response:**
```json
{
  "tier_used": 2,
  "engine": "claude",
  "token_status": {
    "claude": { "used": 24500, "remaining": 975500 }
  }
}
```

---

### Example 3: Emergency (Tier 3)

```bash
curl -X POST http://localhost:8000/api/self/fix-all
```

**When this happens**:
- Claude tokens exhausted (1M+ used)
- System falls back to OpenAI
- GPT-4o handles the issue
- **Cost**: Additional OpenAI tokens

**Response:**
```json
{
  "tier_used": 3,
  "engine": "openai",
  "warning": "OpenAI is final fallback - consider optimizing local patterns",
  "token_status": {
    "claude": { "used": 1000000, "remaining": 0 },
    "openai": { "used": 15000, "remaining": 485000 }
  }
}
```

---

## Slack Commands

All endpoints available via Slack:

```
/piddy self go live
/piddy self fix
/piddy self audit
/piddy self status
```

---

## Best Practices

### 1. **Optimize Tier 1 First**
Add new patterns to `src/self_healing_engine.py` for common issues. This keeps costs down.

### 2. **Monitor Token Usage**
Check `/api/self/status` regularly to see tier distribution:
```bash
curl http://localhost:8000/api/self/status | jq '.healing_system.token_usage'
```

### 3. **Cost Optimization**
- 🟢 Tier 1: Use for 70%+ of fixes
- 🔵 Tier 2: Reserve for complex issues
- 🟠 Tier 3: Emergency only

### 4. **Session Management**
Token limits reset per session. For long-running systems, consider:
- Restarting service periodically
- Setting lower limits for testing
- Monitoring Tier 3 escalation frequency

---

## Troubleshooting

### "Tier 2 unavailable: Claude token limit reached"
→ Escalates to Tier 3 (OpenAI)

### "All AI tiers exhausted"
→ Manual intervention needed or wait for session reset

### "No API key configured"
→ Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to .env

### Local patterns not matching my issue
→ Add new pattern to `src/self_healing_engine.py` and PR it

---

## Cost Summary

| Tier | Cost | Speed | Complexity |
|------|------|-------|------------|
| Tier 1 (Local) | FREE | <1ms | Simple patterns |
| Tier 2 (Claude) | ~$0.01-0.10 | 2-5s | Complex issues |
| Tier 3 (OpenAI) | ~$0.02-0.20 | 3-8s | Emergency |

**Smart Strategy**: Use Tier 1 for 70%+ of issues, Claude for complex ones, OpenAI as fallback.

---

## How It Works (Internal)

```python
# Pseudocode of the tiered logic

async def run_tiered_self_healing():
    # Tier 1: Try local patterns
    result = await tier_1_local_healing()
    if result.success:
        return result  # Done!
    
    # Tier 2: Try Claude if available
    if claude_available and claude_tokens_remaining:
        result = await tier_2_claude_healing()
        if result.success:
            return result  # Done!
    
    # Tier 3: OpenAI final fallback
    result = await tier_3_openai_healing()
    return result  # Always completes
```

---

## Next Steps

1. ✅ Set API keys in `.env` or environment variables
2. ✅ Test with `curl -X POST http://localhost:8000/api/self/fix-all`
3. ✅ Monitor token usage at `/api/self/status`
4. ✅ Optimize Tier 1 patterns for your codebase
5. ✅ Use Slack commands for daily operations

**Piddy will fix itself intelligently - no manual AI prompt engineering needed!** 🚀
