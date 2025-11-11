# Multi-Agent Video Production - Quick Start Guide

## What You're Building

A 4-agent system that transforms VRD documents into production-ready video plans:

```
VRD → ScriptSmith → ShotMaster → VideoSolver → Production Plan
           ↓            ↓            ↓
      ALT Beats    Shot List    Tool Selection
```

---

## Immediate Next Steps

### 1. Review Research Findings

Read the Perplexity research summaries I've gathered:
- ✅ ALT beats structure and best practices
- ✅ Multi-agent handoff patterns  
- ✅ SOTA video generation workflows (2025)
- ✅ Research agent automation strategies

### 2. Review Documentation Created

I've created these reference documents:
- `/ALT_BEATS_SPEC.md` - Complete ALT beats specification
- `/IMPLEMENTATION_PLAN.md` - 6-week phased implementation
- `/Video Solver - Tool Stack.csv` - Your existing tool database

### 3. Enhance ScriptSmith (Week 1 Priority)

Update `/apps/agents/agents/sub_agents.py`:

```python
# Add to ScriptSmith system prompt:
SCRIPTSMITH_SYSTEM_PROMPT = """
You are ScriptSmith, expert in ALT beat generation.

Generate scripts with:
- ALT beats (5-10s each)
- Complete metadata per beat
- JSON + narrative output
- 8-part story structure applied

Each beat must answer: "What does audience need to know NOW?"
"""

# Add new tools:
def generate_alt_beats(vrd: dict) -> dict:
    """Generate complete script with ALT beats"""
    pass

def ask_clarifying_questions(vrd: dict) -> dict:
    """Ask 5 key questions during session"""
    pass
```

### 4. Create ShotMaster Agent (Week 2)

Add new agent to `sub_agents.py`:

```python
def create_shotmaster_agent(llm):
    """Convert ALT beats to detailed shot specs"""
    
    tools = [
        generate_shot_list,
        determine_shot_type,
        design_lighting,
        generate_storyboard
    ]
    
    return create_structured_chat_agent(llm, tools, SHOTMASTER_PROMPT)
```

### 5. Create VideoSolver Agent (Week 3)

Add tool selection agent:

```python
def create_videosolver_agent(llm):
    """Select optimal AI tools per shot"""
    
    tools = [
        query_tool_stack,
        select_optimal_tool,
        calculate_workflow,
        estimate_costs
    ]
    
    return create_structured_chat_agent(llm, tools, VIDEOSOLVER_PROMPT)
```

### 6. Build Deep Research Agent (Week 4)

Create `/apps/agents/research_agent.py`:

```python
async def research_agent_loop():
    """Continuous API discovery and benchmarking"""
    
    while True:
        # Discover new APIs (every 6h)
        new_apis = await discover_apis()
        
        # Benchmark (every 12h)
        results = await benchmark_apis()
        
        # Track SOTA (daily)
        techniques = await track_sota()
        
        # Update database
        await update_tool_stack()
        
        await asyncio.sleep(3600)
```

---

## Key Design Decisions

### From Perplexity Research

**1. Use JSON + Narrative Dual Format**
- Human-readable narrative for review
- Machine-readable JSON for automation
- Both generated simultaneously

**2. Apply 8-Part Story Structure**
```
Hook (5%) → Inciting Event (12%) → 1st Plot Point (25%) →
1st Pinch (37%) → Midpoint (50%) → 2nd Pinch (62%) →
3rd Plot Point (75%) → Climax (90%)
```

**3. SOTA Tool Combinations**
- Wide shots: Google Veo 3 or Sora 2
- Closeups: Kling AI 2.1
- VFX: Runway Gen-4
- Budget: Haiper AI or Luma

**4. Agent Handoff via REST + Streaming**
- Batch: POST /api/agent/endpoint
- Real-time: GRPC or WebSocket streams
- All data: Strongly-typed JSON schemas

---

## Example Workflow

### Input: VRD
```json
{
  "project_name": "SmartHome Hub Launch",
  "duration_seconds": 90,
  "key_messages": {
    "core_message": "Unified smart home control",
    "supporting_messages": [
      "No more app juggling",
      "Works with existing devices",
      "AI learns your routines"
    ]
  }
}
```

### ScriptSmith Output: ALT Beats
```json
{
  "script_id": "script_001",
  "total_beat_count": 17,
  "beats": [
    {
      "beat_id": "1.1",
      "duration_seconds": 5,
      "story_question": "Why should viewer care?",
      "script": {
        "action": "CU alarm clock 6:00 AM. Hand slams down."
      },
      "visual_requirements": {
        "shot_type": "closeup",
        "complexity": "low"
      }
    }
  ]
}
```

### ShotMaster Output: Shot List
```json
{
  "shot_list_id": "shotlist_001",
  "total_shots": 34,
  "shots": [
    {
      "shot_id": "shot_001",
      "beat_ref": "1.1",
      "shot_type": "closeup",
      "camera_movement": "static",
      "lighting": {
        "time_of_day": "early_morning",
        "mood": "harsh"
      },
      "storyboard_frame": {
        "description": "Tight CU on red LED alarm clock",
        "reference_image_prompt": "Close-up red LED alarm 6:00, dim bedroom"
      }
    }
  ]
}
```

### VideoSolver Output: Production Plan
```json
{
  "production_plan_id": "plan_001",
  "total_cost_usd": 24.50,
  "total_time_minutes": 45,
  "shot_plans": [
    {
      "shot_id": "shot_001",
      "recommended_workflow": {
        "steps": [
          {
            "tool": "midjourney_v6",
            "purpose": "Generate static image",
            "cost_usd": 0.04
          },
          {
            "tool": "runway_gen3",
            "purpose": "Add hand motion",
            "cost_usd": 0.10
          }
        ],
        "total_cost": 0.14,
        "quality_score": 9.3
      }
    }
  ]
}
```

---

## Testing Strategy

### Phase 1: Unit Tests
```python
def test_scriptsmith_generates_alt_beats():
    vrd = load_test_vrd()
    script = generate_alt_beats(vrd, {})
    
    assert script['total_beat_count'] > 0
    assert all('beat_id' in b for b in script['beats'])
    assert all('visual_requirements' in b for b in script['beats'])
```

### Phase 2: Integration Tests
```python
async def test_full_pipeline():
    vrd = load_test_vrd()
    
    # ScriptSmith
    script = await scriptsmith.generate(vrd)
    assert script['script_id']
    
    # ShotMaster
    shots = await shotmaster.generate(script['beats'])
    assert shots['shot_list_id']
    
    # VideoSolver
    plan = await videosolver.plan(shots['shots'])
    assert plan['production_plan_id']
    assert plan['total_cost_usd'] > 0
```

---

## Success Metrics

### Week 1: ScriptSmith
- ✅ Generates valid JSON ALT beats
- ✅ Asks 5 clarifying questions
- ✅ Applies 8-part structure correctly
- ✅ Timing within ±5s of VRD

### Week 2: ShotMaster
- ✅ Converts beats to 30+ shots
- ✅ Provides detailed specifications
- ✅ Generates storyboard descriptions
- ✅ Maintains visual continuity

### Week 3: VideoSolver
- ✅ Selects optimal tools per shot
- ✅ Defines complete workflows
- ✅ Calculates accurate costs
- ✅ Provides alternative options

### Week 4: Research Agent
- ✅ Discovers 5+ new APIs per week
- ✅ Benchmarks all major tools
- ✅ Tracks SOTA combinations
- ✅ Updates database automatically

---

## Resources Created

1. **ALT_BEATS_SPEC.md** - Complete specification
2. **IMPLEMENTATION_PLAN.md** - 6-week roadmap
3. **QUICK_START_GUIDE.md** - This file
4. **scriptsmith.md** - Enhanced knowledge base (v2.0)

---

## Get Started Now

1. ✅ Review Perplexity research findings (above)
2. ✅ Read ALT_BEATS_SPEC.md
3. ✅ Read IMPLEMENTATION_PLAN.md
4. → **Start Week 1**: Enhance ScriptSmith
5. → Test with example VRD
6. → Iterate and refine

**First Code Change**: Update ScriptSmith system prompt in `sub_agents.py` to include ALT beats methodology.

---

Good luck! The research is done, the plan is clear, now it's time to build. 🚀
