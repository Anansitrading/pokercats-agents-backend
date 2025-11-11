# Merge-00: Integration Overview & Git Workflow

**Created:** 2025-01-06 00:45 UTC+01:00  
**Objective:** Integrate LangGraph agents system with existing Next.js video editor  
**Status:** Pre-integration planning

---

## 🎯 Current Situation

### System 1: Working Video Editor (Main Branch)
**Location:** `PokerCats/apps/web/`  
**Stack:** Next.js 15, React, TypeScript, Zustand, Drizzle ORM  
**Features:**
- Full browser-based video editor
- Timeline with tracks and clips
- Media panel with assets
- Gemini Live integration (voice + image/video generation)
- OPFS storage for large files
- IndexedDB for projects

**Key Files:**
- `apps/web/src/components/kijko-agent/RightPanel.tsx` - Chat UI with Gemini
- `apps/web/src/stores/gemini-agent-store.ts` - Asset & chat state
- `apps/web/src/services/geminiService.ts` - Gemini API calls
- `apps/web/src/components/editor/timeline/` - Timeline components
- `packages/db/`, `packages/ai/`, `packages/auth/` - Shared packages

### System 2: LangGraph Agents (Feature Branch)
**Location:** `PokerCats/apps/agents/`  
**Stack:** FastAPI, Python, LangGraph, OpenAI, Gemini  
**Features:**
- Supervisor agent with 4 sub-agents
- VRD, ScriptSmith, ShotMaster, VideoSolver
- Graceful degradation with observability
- Structured logging (JSON)
- Startup validation

**Key Files:**
- `apps/agents/main.py` - FastAPI server
- `apps/agents/agents/supervisor.py` - LangGraph supervisor
- `apps/agents/agents/enhanced_sub_agents.py` - Enhanced agents
- `apps/agents/agents/observability.py` - Logging & metrics
- `apps/agents/tools/` - Modular tools (ALT beats, shot planning, tool selection)

### The Problem
**Zero Integration:** The two systems are completely separate. No code connects them.

---

## 🔄 Git Workflow: Merge Main Into Feature Branch

### Prerequisites
```bash
# Verify current branch
git branch --show-current
# Should show: feature/multi-agent-system (or similar)

# Check git status
git status
# Ensure all agent system changes are committed
```

### Step 1: Commit Current Work
```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat(agents): Add observability and graceful degradation

- Structured JSON logging with observability.py
- Startup validation with clear warnings
- VRD functions extracted to dedicated module
- Supervisor tracks all fallback usage
- Session metrics on shutdown

Sprint 2.5 complete. Ready for integration with main branch video editor."

# Push to remote
git push origin feature/multi-agent-system
```

### Step 2: Fetch Latest Main
```bash
# Fetch all remote branches
git fetch origin

# View what's changed on main (optional)
git log HEAD..origin/main --oneline
```

### Step 3: Merge Main Into Feature Branch
```bash
# Ensure you're on feature branch
git checkout feature/multi-agent-system

# Merge main INTO your feature branch
git merge origin/main

# If no conflicts:
# - Auto merge commit created
# - All main code now in feature branch

# If conflicts appear:
# - Git will pause and mark conflicted files
# - See "Conflict Resolution" section below
```

### Step 4: Verify Main Code Present
```bash
# Check that web app files are present
ls -la apps/web/src/components/editor/
ls -la packages/

# Test the web app still works
cd apps/web
npm install  # if package.json changed
npm run dev

# Test agents system still works
cd ../agents
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Step 5: Push Merged Branch
```bash
# Push merged feature branch
git push origin feature/multi-agent-system
```

---

## ⚠️ Conflict Resolution

### Expected Conflicts
Most likely **ZERO conflicts** because:
- Agent system is in new `apps/agents/` directory
- Main branch doesn't have this directory
- No overlapping files

### If Conflicts Occur
```bash
# Git will show conflicted files
git status

# Common conflict locations:
# - package.json (if both added dependencies)
# - turbo.json (if both modified)
# - .gitignore (if both added patterns)

# Resolve each file:
# 1. Open file in editor
# 2. Look for conflict markers:
#    <<<<<<< HEAD (your changes)
#    =======
#    >>>>>>> origin/main (main branch)
# 3. Keep BOTH changes (merge manually)
# 4. Remove conflict markers

# Example: package.json conflict
# BEFORE:
# <<<<<<< HEAD
#   "scripts": { "agents": "cd apps/agents && uvicorn main:app" }
# =======
#   "scripts": { "web": "cd apps/web && npm run dev" }
# >>>>>>> origin/main

# AFTER (keep both):
# "scripts": {
#   "web": "cd apps/web && npm run dev",
#   "agents": "cd apps/agents && uvicorn main:app"
# }

# Stage resolved files
git add <resolved-file>

# Complete merge
git commit
```

### Abort Merge If Needed
```bash
# If merge goes wrong, abort and try again
git merge --abort

# This returns to pre-merge state
```

---

## ✅ Verification Checklist

After merge, verify:

- [ ] `apps/web/` directory exists with video editor
- [ ] `apps/agents/` directory exists with LangGraph system
- [ ] `packages/db/`, `packages/ai/`, `packages/auth/` exist
- [ ] `git log` shows merge commit
- [ ] `git status` shows clean working tree
- [ ] Web app runs: `cd apps/web && npm run dev`
- [ ] Agents run: `cd apps/agents && python -m uvicorn main:app`
- [ ] Main branch unchanged: `git log origin/main` (no new commits)

---

## 📋 Next Steps

After successful merge:

1. **Read:** `Merge-01-Architecture.md` - Integration architecture
2. **Read:** `Merge-02-API-Bridge.md` - API client implementation
3. **Read:** `Merge-03-WebSocket.md` - Real-time streaming
4. **Read:** `Merge-04-UI-Integration.md` - Update React components
5. **Read:** `Merge-05-Testing.md` - End-to-end testing plan

---

## 🚨 Important Notes

### DO NOT Merge Back to Main
```bash
# ❌ NEVER DO THIS (yet):
git checkout main
git merge feature/multi-agent-system

# Main branch stays pristine until integration is complete and tested
```

### Keep Feature Branch Updated
```bash
# Periodically (daily/weekly), merge main into feature:
git checkout feature/multi-agent-system
git fetch origin
git merge origin/main
git push origin feature/multi-agent-system
```

### Backup Before Merge
```bash
# Optional: Create backup branch
git branch feature/multi-agent-system-backup
```

---

## 📊 File Structure After Merge

```
PokerCats/
├── apps/
│   ├── web/                    # ← From main (Next.js video editor)
│   │   ├── src/
│   │   │   ├── components/     # React components
│   │   │   ├── stores/         # Zustand stores
│   │   │   ├── services/       # API services
│   │   │   └── app/            # Next.js app router
│   │   └── package.json
│   │
│   ├── agents/                 # ← From feature (LangGraph agents)
│   │   ├── agents/             # Agent modules
│   │   ├── tools/              # Modular tools
│   │   ├── routes/             # FastAPI routes
│   │   ├── main.py             # FastAPI app
│   │   └── requirements.txt
│   │
│   └── transcription/          # ← From main
│
├── packages/                   # ← From main (shared monorepo packages)
│   ├── db/                     # Drizzle ORM
│   ├── ai/                     # AI services
│   └── auth/                   # Better Auth
│
└── turbo.json                  # ← Merge both if conflict
```

---

**Status:** Ready for git merge  
**Next:** Run git workflow above, then proceed to Merge-01-Architecture.md
