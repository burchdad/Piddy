# 🚀 Piddy Deployment Guide (Vercel + Backend Service)

## Architecture

```
Frontend (Vercel)  ←→  Backend API (Render/Railway/Fly.io)
  React Dashboard       FastAPI + Docker
```

---

## Frontend Deployment to Vercel

### Option A: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

Vercel will:
- Detect `vercel.json` configuration
- Build only the frontend (`frontend/dist`)
- Deploy to `your-domain.vercel.app`

### Option B: Deploy via GitHub

1. Push to GitHub: `git push`
2. Go to https://vercel.com/new
3. Import from GitHub
4. Set Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-url.com` (e.g., from Render/Railway/Fly.io)

---

## Backend Deployment (Choose One)

### Option 1: Deploy to Render (Recommended - Easiest)

1. Push your repo to GitHub
2. Go to https://render.com
3. Click "New" → "Web Service"
4. Connect GitHub repository
5. Fill in:
   - **Name**: `piddy-backend`
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Root Directory**: `.` (leave as is)
6. Click "Create Web Service"
7. Render builds and deploys automatically
8. Copy the URL (e.g., `https://piddy-backend.onrender.com`)

**Connect Frontend to Backend:**
- In Vercel dashboard → Project Settings → Environment Variables
- Add `VITE_API_URL=https://piddy-backend.onrender.com`
- Redeploy frontend

### Option 2: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your Piddy repository
4. Railway auto-detects Docker setup
5. Configure:
   - Set environment variables from `.env`
   - Railway generates public URL
6. Copy the URL and add to Vercel

### Option 3: Deploy to Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Create app: `flyctl launch`
4. Deploy: `flyctl deploy`
5. Get URL: `flyctl info`

---

## Environment Variables

### Vercel (Frontend)
```
VITE_API_URL=https://piddy-backend.onrender.com
```

### Render/Railway/Fly.io (Backend)
```
SLACK_BOT_TOKEN=your_token
SLACK_SIGNING_SECRET=your_secret
SLACK_APP_TOKEN=your_token
ANTHROPIC_API_KEY=your_key
DATABASE_URL=sqlite:///./piddy.db
DEBUG=False
```

---

## Testing Deployment

1. Open frontend: `https://your-domain.vercel.app`
2. Check browser console (F12)
3. Should see: `✅ System status fetched`
4. All dashboard tabs should display real data

---

## Troubleshooting

### Frontend loads but no data
- Check browser console for errors
- Verify `VITE_API_URL` is set correctly in Vercel
- Ensure backend is accessible (check backend service status)
- Test API directly: `curl https://piddy-backend.onrender.com/api/logs`

### CORS errors
- Backend should have CORS enabled (FastAPI already does via `CORSMiddleware`)
- Verify backend is responding to requests

### Backend keeps restarting on free tier
- Free tier instances sleep after inactivity
- Consider upgrading or using GitHub Actions to ping the backend

---

## Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render/Railway/Fly.io
- [ ] `VITE_API_URL` environment variable set in Vercel
- [ ] Frontend loads without errors
- [ ] Dashboard displays real data
- [ ] All API endpoints responding
- [ ] Rate limiting monitoring working
- [ ] Logs component showing real logs

---

## Keeping Backend Awake (Free Tier)

If using free tier (prone to sleeping), create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Backend Alive

on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping backend
        run: curl https://piddy-backend.onrender.com/api/logs
```

This keeps the backend service active!
