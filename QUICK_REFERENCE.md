# Quick Reference - Sprint 2.5 Integration

**For Developers**: Fast lookup for common tasks

---

## 🚀 Getting Started (60 seconds)

```bash
# 1. Install
cd /home/david/Projects/MVP/PokerCats/apps/agents
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
echo "MODEL_PROVIDER=google" >> .env
echo "GOOGLE_API_KEY=your-key-here" >> .env

# 3. Run
python -m uvicorn main:app --reload --port 8000

# 4. Test
curl http://localhost:8000/health
curl http://localhost:8000/agents/voice/status
```

---

## 📝 Environment Variables

```bash
# Required
MODEL_PROVIDER=google              # or "openai"
GOOGLE_API_KEY=AIza...             # From Google AI Studio

# Optional
OPENAI_API_KEY=sk-...              # Fallback
DATABASE_URL=postgresql://...       # For persistence
```

---

## 🎯 API Endpoints

### Text API

```bash
# Invoke (blocking)
POST /agents/execute/invoke
{
  "message": "Create a 60s product demo video",
  "thread_id": "optional-thread-id",
  "user_context": {}
}

# Stream (SSE)
POST /agents/execute/stream
# Same body, returns Server-Sent Events
```

### Voice API

```bash
# Status
GET /agents/voice/status

# WebSocket
WS /agents/voice/live
# Send: Audio chunks (PCM 16kHz)
# Receive: Audio + transcriptions + tool events
```

---

## 🛠️ Model Selection

### Per Provider

```python
from agents.model_factory import get_model

# Gemini (recommended)
model = get_model(provider="google", task_type="reasoning")
# → gemini-2.5-pro

model = get_model(provider="google", task_type="repetitive")
# → gemini-2.5-flash

# OpenAI (fallback)
model = get_model(provider="openai", task_type="reasoning")
# → gpt-4o
```

### Per Agent

```python
from agents.model_factory import get_agent_model

supervisor_model = get_agent_model("supervisor", provider="google")
# → gemini-2.5-pro (reasoning task)

solver_model = get_agent_model("video_solver_agent", provider="google")
# → gemini-2.5-flash (repetitive task)
```

### Cost Comparison

| Provider | Model | Cost per 1M tokens | Use Case |
|----------|-------|-------------------|----------|
| Google | gemini-2.5-pro | $1.25 | Reasoning, creative |
| Google | gemini-2.5-flash | $0.075 | Repetitive, voice |
| OpenAI | gpt-4o | $2.50 | Reasoning (fallback) |
| OpenAI | gpt-4o-mini | $0.15 | Repetitive (fallback) |

---

## 🎬 Usage Patterns

### Pattern 1: YOLO Mode (Full Auto)

```python
from workflows import ProductionOrchestrator

orchestrator = ProductionOrchestrator(mode="yolo")

vrd = {
    "video_type": "product_demo",
    "estimated_duration": "60s",
    "target_audience": "B2B decision makers",
    "tone": "professional"
}

result = orchestrator.execute_full_pipeline(vrd)

print(f"Beats: {result['summary']['beats']}")
print(f"Shots: {result['summary']['shots']}")
print(f"Cost: ${result['summary']['cost_usd']}")
```

**Output**:
```
Beats: 8
Shots: 14
Cost: $12.45
Time: 25.3 minutes
```

### Pattern 2: HITL Mode (Interactive)

```python
orchestrator = ProductionOrchestrator(mode="hitl")

# Step 1: VRD
status = orchestrator.set_vrd(vrd)
if status['status'] == 'needs_clarification':
    questions = status['questions']
    # Display to user, get answers
    orchestrator.provide_clarifications(answers)

# Step 2: Script (approval required)
script_result = orchestrator.generate_script()
# User reviews and approves

# Step 3: Shots (approval required)
shots_result = orchestrator.generate_shots()
# User reviews and approves

# Step 4: Plan
plan_result = orchestrator.generate_plan()
```

### Pattern 3: Voice Agent

```javascript
// Frontend code
const ws = new WebSocket('ws://localhost:8000/agents/voice/live')

// Send audio
ws.send(audioChunkPCM16kHz)

// Receive events
ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Audio response
    playAudio(event.data)
  } else {
    const msg = JSON.parse(event.data)
    if (msg.type === 'transcription') {
      console.log(msg.role, msg.text)
    }
    if (msg.type === 'tool_call') {
      console.log('Calling tool:', msg.tool)
    }
  }
}
```

---

## 🧩 Component Integration

### Enhanced Agents

```python
# Automatically used if available
from agents.supervisor import get_supervisor_workflow

workflow = get_supervisor_workflow()
# Uses enhanced agents if modular tools installed
# Falls back to legacy if not
```

### Direct Tool Access

```python
# Use modular tools directly
from tools import generate_alt_beats, generate_shot_list, generate_production_plan
from models.alt_beat import Script

# Generate script
script = generate_alt_beats(vrd, mode="yolo")

# Generate shots
shot_list = generate_shot_list(script.beats, mode="yolo")

# Generate plan
plan = generate_production_plan(
    shot_list,
    constraints={'quality_priority': 'high'},
    mode="yolo"
)

# Access type-safe data
print(f"Beat 1: {script.beats[0].story_question}")
print(f"Shot 1: {shot_list.shots[0].shot_type}")
print(f"Cost: ${plan.total_estimated_cost_usd}")
```

---

## 🔍 Debugging

### Check Model Provider

```python
import os
print(f"Provider: {os.getenv('MODEL_PROVIDER', 'not set')}")
print(f"Google API: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}")
print(f"OpenAI API: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
```

### Check Enhanced Agents

```python
from agents.supervisor import ENHANCED_AGENTS_AVAILABLE
print(f"Enhanced agents: {'✅' if ENHANCED_AGENTS_AVAILABLE else '❌'}")

from agents.enhanced_sub_agents import MODULAR_TOOLS_AVAILABLE
print(f"Modular tools: {'✅' if MODULAR_TOOLS_AVAILABLE else '❌'}")
```

### Check Voice Agent

```bash
curl http://localhost:8000/agents/voice/status | jq

{
  "available": true,
  "model": "gemini-2.5-flash-preview-0205",
  "features": ["real_time_voice", "tool_calling", ...]
}
```

### View Logs

```bash
# Server logs show:
✅ Using enhanced agents with modular tools
✅ Supervisor workflow initialized with all sub-agents
✅ Voice agent available with tool calling
```

---

## 🧪 Testing

### Unit Tests

```python
# Test model selection
def test_model_factory():
    from agents.model_factory import get_model
    model = get_model(provider="google", task_type="reasoning")
    assert "gemini-2.5-pro" in str(model)

# Test enhanced agents
def test_enhanced_agents():
    from agents.enhanced_sub_agents import create_enhanced_script_smith_agent
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    agent = create_enhanced_script_smith_agent(model)
    assert agent is not None
```

### Integration Test

```python
def test_full_pipeline():
    from workflows import ProductionOrchestrator
    
    orchestrator = ProductionOrchestrator(mode="yolo")
    vrd = {
        "video_type": "explainer",
        "estimated_duration": "60s"
    }
    
    result = orchestrator.execute_full_pipeline(vrd)
    
    assert result['status'] == 'pipeline_complete'
    assert result['summary']['beats'] == 8
    assert result['summary']['cost_usd'] > 0
```

### Voice Test

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c ws://localhost:8000/agents/voice/live

# Send test
> {"text": "Create a video script"}

# Observe tool calls and responses
```

---

## 📊 Performance Benchmarks

Expected performance (60s video, YOLO mode):

| Stage | Time | Notes |
|-------|------|-------|
| Model init | ~1s | One-time |
| VRD analysis | ~2s | Gemini Pro |
| ALT beats | ~4s | 8 beats with metadata |
| Shot planning | ~3s | 14 shots |
| Production plan | ~2s | Tool selection |
| **Total** | **~12s** | End-to-end |

Voice latency: <500ms

---

## 🐛 Common Issues

### "ModuleNotFoundError: No module named 'tools'"

```bash
# Install Pydantic
pip install pydantic>=2.0.0

# Verify path
cd /home/david/Projects/MVP/PokerCats/apps/agents
python -c "from tools import generate_alt_beats; print('✅ Tools available')"
```

### "Google API Key not set"

```bash
# Check .env
cat .env | grep GOOGLE_API_KEY

# Set if missing
export GOOGLE_API_KEY=your-key-here

# Or add to .env
echo "GOOGLE_API_KEY=your-key" >> .env
```

### "Voice agent not available"

```bash
# Install Gemini SDK
pip install google-generativeai>=0.8.0

# Verify
python -c "from google import genai; print('✅ Gemini SDK installed')"
```

### "Enhanced agents not available"

```bash
# Check imports
python -c "from agents.enhanced_sub_agents import create_enhanced_script_smith_agent; print('✅ Enhanced agents work')"

# If fails, check models and tools are importable
python -c "from models.alt_beat import Script; print('✅ Models work')"
python -c "from tools import generate_alt_beats; print('✅ Tools work')"
```

---

## 📁 File Structure

```
apps/agents/
├── agents/                     # Agent implementations
│   ├── model_factory.py       # ✨ NEW: Model selection
│   ├── enhanced_sub_agents.py # ✨ NEW: Tool integration
│   ├── supervisor.py          # UPDATED: Uses factory
│   └── sub_agents.py          # Legacy (fallback)
│
├── routes/                     # API endpoints
│   ├── execute.py             # Text API
│   └── voice.py               # ✨ NEW: Voice WebSocket
│
├── models/                     # ✨ NEW: Type-safe models
│   ├── alt_beat.py
│   ├── shot.py
│   └── production_plan.py
│
├── tools/                      # ✨ NEW: Business logic
│   ├── alt_beat_generator.py
│   ├── shot_planner.py
│   └── tool_selector.py
│
├── workflows/                  # ✨ NEW: Orchestration
│   └── production_orchestrator.py
│
├── .env.example               # UPDATED: Google API key
├── requirements.txt           # UPDATED: Gemini SDK
└── main.py                    # UPDATED: Voice routes
```

---

## 🎓 Key Concepts

**ALT Beats**: Atomic narrative units with complete metadata
- 5-10 seconds each
- Question-answer structure
- Visual/audio/emotional specs
- Production requirements

**8-Part Structure**: Hook → Inciting Event → Plot Points → Midpoint → Climax
- Scientifically validated narrative framework
- Timing calculated as % of total duration
- Each position has specific emotional function

**Model Factory**: Intelligent model selection
- Task-based (reasoning, repetitive, creative)
- Provider-based (Google, OpenAI)
- Cost optimization (97% reduction for simple tasks)

**Enhanced Agents**: Bridge layer
- LangGraph agents → Modular tools
- Type-safe parameters (Pydantic)
- Graceful fallback to legacy

**Voice Agent**: Gemini Live API integration
- Real-time bidirectional streaming
- Tool calling during conversation
- Sub-500ms latency

---

## 🚦 Status Indicators

**System Ready**:
```
✅ Using enhanced agents with modular tools
✅ Supervisor workflow initialized
✅ Voice agent available
```

**Fallback Mode**:
```
⚠️ Enhanced agents not available
⚠️ Using legacy tools
⚠️ Voice agent not available
```

**Error State**:
```
❌ Google API Key not configured
❌ Models not importable
❌ Database connection failed
```

---

## 📖 Further Reading

- **SPRINT_2.5_COMPLETE.md**: Complete integration guide
- **SPRINT_2_FINAL_ASSESSMENT.md**: Gap resolution details
- **ARCHITECTURE.md**: System design documentation
- **NEW_SYSTEM_GUIDE.md**: Modular tools guide

---

**Last Updated**: November 6, 2025  
**Version**: Sprint 2.5  
**Status**: Production Ready ✅
