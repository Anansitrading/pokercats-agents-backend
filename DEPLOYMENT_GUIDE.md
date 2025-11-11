# PokerCats Agents Backend - Deployment Guide

## 🎯 Repository Created Successfully

Your backend code has been extracted to a separate repository at:
```
/home/david/Projects/MVP/pokercats-agents-backend/
```

Git repository initialized with initial commit ✅

## 📦 Next Steps: Create GitHub Remote

### Option 1: Using GitHub CLI (gh)

```bash
cd /home/david/Projects/MVP/pokercats-agents-backend

# Login to GitHub (if not already logged in)
gh auth login

# Create the remote repository
gh repo create pokercats-agents-backend \
  --public \
  --source=. \
  --remote=origin \
  --push
```

### Option 2: Using GitHub Web UI

1. Go to https://github.com/new
2. Repository name: `pokercats-agents-backend`
3. Description: "Multi-agent orchestration backend for PokerCats video production"
4. Choose Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

Then connect your local repo:
```bash
cd /home/david/Projects/MVP/pokercats-agents-backend
git remote add origin https://github.com/YOUR_USERNAME/pokercats-agents-backend.git
git push -u origin main
```

## 🚀 Deploy to Railway

### Update Railway Project

Your current Railway deployment at `https://mvp20-production.up.railway.app` needs to point to the new repo.

**Option A: Update Existing Project**
```bash
# In the new backend directory
railway link

# Select your existing project: mvp20-production
# Railway will auto-detect the changes

railway up
```

**Option B: Create New Railway Project**
```bash
cd /home/david/Projects/MVP/pokercats-agents-backend

# Login to Railway
railway login

# Create new project
railway init

# Deploy
railway up
```

### Environment Variables on Railway

Ensure these are set in Railway dashboard:
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `OPENAI_API_KEY` - (Optional) OpenAI API key for fallback
- `DATABASE_URL` - (Optional) PostgreSQL connection string
- `MODEL_PROVIDER` - Set to "google" or "openai"

## ✅ Verification Checklist

### Local Testing
```bash
cd /home/david/Projects/MVP/pokercats-agents-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python main.py
```

Test the server:
```bash
# Health check
curl http://localhost:8000/health

# Test SSE endpoint
curl -N -X POST http://localhost:8000/agents/execute/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"test","thread_id":"test123"}'
```

### Frontend Integration Test

1. Keep your current `/home/david/Projects/MVP/PokerCats/apps/agents/` **INTACT** (don't delete yet)
2. Deploy the new repo to Railway
3. Update Railway URL in your frontend if needed (it should stay the same)
4. Test the SSE test client at `/home/david/Projects/MVP/PokerCats/test-sse-client.html`
5. Verify events are streaming correctly

## 📋 What Was Copied

```
pokercats-agents-backend/
├── .gitignore              ✅ NEW
├── README.md               ✅ Complete documentation
├── DEPLOYMENT_GUIDE.md     ✅ NEW (this file)
├── requirements.txt        ✅ All dependencies
├── railway.toml            ✅ Railway config
├── .env.example           ✅ Environment template
├── main.py                 ✅ FastAPI entry point
├── agents/                 ✅ All agent code
│   ├── supervisor.py
│   ├── model_factory.py
│   ├── enhanced_sub_agents.py
│   ├── sub_agents.py
│   └── ...
├── routes/                 ✅ API routes
│   ├── execute.py         (SSE streaming endpoint)
│   └── voice.py
├── models/                 ✅ Data models
├── tools/                  ✅ Agent tools
└── workflows/              ✅ Orchestration workflows
```

## ⚠️ Important Notes

1. **DO NOT DELETE** `/home/david/Projects/MVP/PokerCats/apps/agents/` until you confirm:
   - ✅ Remote repo created and pushed
   - ✅ Railway deployed successfully
   - ✅ Frontend test client works with new deployment
   - ✅ All environment variables set correctly

2. **Frontend will NOT be affected** because it connects to the Railway URL, not the local code path

3. **Railway Token**: You have `f4fa39a1-11fb-45fc-a12a-96742a00793e` - use this to link/deploy

## 🔗 Links After Setup

- **Repository**: `https://github.com/YOUR_USERNAME/pokercats-agents-backend`
- **Railway Dashboard**: `https://railway.app/dashboard`
- **Deployed API**: `https://mvp20-production.up.railway.app` (should remain the same)
- **API Docs**: `https://mvp20-production.up.railway.app/docs`

## 🐛 Troubleshooting

### If deployment fails:
```bash
# Check logs
railway logs

# Verify environment variables
railway variables

# Restart service
railway restart
```

### If frontend can't connect:
1. Check CORS settings in `main.py` (should allow all origins currently)
2. Verify Railway deployment URL matches frontend config
3. Check Railway logs for errors
