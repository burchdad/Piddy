# ⚡ Tiered Healing: Quick Reference

## One-Liners

### Auto-Tiered (Recommended)
```bash
curl -X POST http://localhost:8000/api/self/fix-all
```
Let Piddy choose the best tier automatically.

### Local Only (Fast & Free)
```bash
curl -X POST http://localhost:8000/api/self/fix-all-local
```
Pattern-based fixes only, zero cost.

### Claude Only
```bash
curl -X POST http://localhost:8000/api/self/fix-claude
```
Skip local, go straight to Claude analysis.

### OpenAI Only (Emergency)
```bash
curl -X POST http://localhost:8000/api/self/fix-openai
```
Use GPT-4o as last resort.

### Check Status
```bash
curl http://localhost:8000/api/self/status | jq '.healing_system'
```
See token usage and tier availability.

---

## Cost Breakdown

| Tier | Cost | Speed | When to Use |
|------|------|-------|------------|
| 1 | FREE | <1ms | Default |
| 2 | ~$0.01 | 2-5s | Complex issues |
| 3 | ~$0.02 | 3-8s | Emergency |

---

## Decision Tree

```
Start: curl -X POST /api/self/fix-all

Is it a simple issue? YES → Tier 1 ✅ ($0.00)
                    NO ↓
Is Claude available? YES → Tier 2 ✅ (~$0.01)
                    NO ↓
Use OpenAI          → Tier 3 ✅ (~$0.02)
```

---

## Response Examples

### Tier 1 Success
```json
{
  "tier_used": 1,
  "engine": "local_self_healing",
  "uses_external_ai": false,
  "ai_cost": "FREE"
}
```

### Tier 2 Used
```json
{
  "tier_used": 2,
  "engine": "claude",
  "tokens_used": 24500,
  "token_status": { "remaining": 975500 }
}
```

### Tier 3 Used (Last Resort)
```json
{
  "tier_used": 3,
  "engine": "openai",
  "tokens_used": 45000,
  "warning": "Claude tokens exhausted, using OpenAI"
}
```

---

## Setup

### 1. Add Keys to `.env`
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 2. Test It
```bash
curl http://localhost:8000/api/self/status
```

### 3. Deploy
```bash
git push origin main  # Goes to Railway/Vercel
```

---

## All Endpoints

```
GET    /api/self/status           Check tier status & tokens
POST   /api/self/audit            System audit
POST   /api/self/fix-all          Auto-tiered (smart)
POST   /api/self/fix-all-local    Tier 1 only
POST   /api/self/fix-claude       Tier 2 only  
POST   /api/self/fix-openai       Tier 3 only
POST   /api/self/go-live          Full deployment
```

---

## In 10 Seconds

1. Piddy tries **local patterns** first → Works 70% of the time (FREE)
2. If that fails, tries **Claude** → Works 25% of the time (cheap)
3. If that fails, uses **OpenAI** → Works 100% of the time (final fallback)

That's it! Piddy auto-heals itself intelligently. 🚀

---

For detailed info: See [TIERED_HEALING_SYSTEM.md](TIERED_HEALING_SYSTEM.md)
