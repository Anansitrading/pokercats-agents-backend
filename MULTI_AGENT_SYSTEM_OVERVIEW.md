# Multi-Agent Video Production System - Complete Overview

## Executive Summary

Based on comprehensive Perplexity research, this document outlines the complete ALT beats-based multi-agent video production system with four specialized agents and continuous tool discovery.

---

## What Are ALT Beats?

**ALT (Alternative) Beats** are structured narrative units specifically designed for AI-driven video production:

- **Atomic**: Each beat does ONE thing clearly
- **Question-Driven**: Answers "what does the audience need to know RIGHT NOW?"
- **Metadata-Rich**: Complete specifications (timing, visual, audio, emotion)
- **Machine-Readable**: JSON format for agent consumption
- **Human-Readable**: Narrative remains understandable

**Why They Matter:**
Traditional scripts are for human directors. ALT beats bridge creative storytelling with AI automation by providing exact timecodes, complete visual specifications, audio requirements, emotional context, and production metadata for optimal tool selection.

---

## System Architecture

### The Four-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  VIDEO PRODUCTION PIPELINE                    │
└─────────────────────────────────────────────────────────────┘

1. ChatVRD (Existing)
   └─→ Outputs: VRD document
   
2. ScriptSmith (Enhanced)
   ├─→ Consumes: VRD + scriptsmith.md knowledge
   ├─→ Process: Asks clarifying questions
   └─→ Outputs: Script with ALT beats (JSON + narrative)
   
3. ShotMaster (New)
   ├─→ Consumes: ALT beats from ScriptSmith
   ├─→ Process: Generates shot specifications and storyboards
   └─→ Outputs: Detailed shot list with technical requirements
   
4. VideoSolver (New)
   ├─→ Consumes: Shot list from ShotMaster
   ├─→ Process: Queries Tool Stack, selects optimal workflows
   └─→ Outputs: Production plan with cost/time estimates

┌─────────────────────────────────────────────────────────────┐
│              CONTINUOUS BACKGROUND PROCESS                    │
└─────────────────────────────────────────────────────────────┘

5. Deep Research Agent (New)
   ├─→ Discovers: New video generation APIs (every 6 hours)
   ├─→ Benchmarks: Quality, cost, speed (every 12 hours)
   ├─→ Tracks: SOTA techniques (daily)
   └─→ Updates: Tool Stack database automatically
```

---

## Key Research Findings

### 1. ALT Beats Best Practices (from Perplexity)

**Structure Requirements:**
- **5-10 seconds per beat** for optimal AI generation
- **Metadata tags**: emotion, character, visual context, camera direction
- **Hierarchical organization**: Chronological within acts
- **Explicit question-answer framing**: Clear mapping for AI selection
- **Information density**: Short, distinct, unambiguous descriptions

**Example Beat:**
```json
{
  "beat_id": "1.3",
  "timecode_start": "00:00:10:00",
  "timecode_end": "00:00:15:00",
  "duration_seconds": 5,
  "story_question": "What problem is the character facing?",
  "story_answer": "Smart home systems are fragmented",
  "script": {
    "action": "BATHROOM. Maya adjusts shower. Water goes ICE COLD.",
    "dialogue": "Not again!"
  },
  "visual_requirements": {
    "shot_type": "medium_closeup",
    "camera_movement": "static",
    "lighting": "morning_natural"
  },
  "emotional_context": {
    "character_emotion": "frustrated",
    "intensity": 7
  },
  "narrative_function": {
    "eight_part_position": "inciting_event"
  }
}
```

### 2. Multi-Agent Handoff Patterns (from Perplexity)

**Best Practices:**
- **Prompt Chaining**: Sequential agent calls, each refining previous output
- **Orchestration**: Master controller initiates agents by domain
- **REST for Batch**: POST/PUT for complete data transfer
- **GRPC/WebSocket for Streaming**: Real-time bidirectional updates
- **Strongly-Typed Schemas**: JSON with explicit references and metadata
- **Provenance Tracking**: Log prompts and edit history for every asset

**Data Exchange Format:**
```json
{
  "agent_output": {
    "output_id": "unique_id",
    "source_agent": "scriptsmith",
    "target_agent": "shotmaster",
    "timestamp": "2025-11-06T00:00:00Z",
    "data": { /* structured payload */ },
    "metadata": { /* provenance info */ }
  }
}
```

### 3. SOTA Video Generation Workflows 2025 (from Perplexity)

**Tool Rankings by Use Case:**

| Use Case | Best Tool | Quality Score | Cost/Second | Key Strengths |
|----------|-----------|---------------|-------------|---------------|
| Wide shots, cinematic | Google Veo 3 | 9.7/10 | TBA | 4K, physics realism, native audio |
| Long-form storytelling | OpenAI Sora 2 | 9.6/10 | TBA | 60s duration, scene continuity |
| Closeups, lip-sync | Kling AI 2.1 | 9.2/10 | $0.06 | Photorealism, facial accuracy |
| Stylized VFX | Runway Gen-4 | 9.3/10 | $0.05 | Character consistency, effects |
| Fast ad clips | Luma Dream Machine | 9.1/10 | $0.08 | Accelerated rendering, cinematic |
| Budget-friendly | Haiper AI | 8.6/10 | $0.05 | Fast generation, decent quality |

**SOTA Workflow Combinations:**
- **Professional Quality**: Veo/Sora for wide shots → Kling for closeups → Runway for VFX
- **Budget Conscious**: Stable Diffusion XL for stills → Haiper for animation
- **Speed Priority**: Luma Dream Machine for all shots (consistency over max quality)

**Shot Type Recommendations:**
- **Extreme Closeup (ECU)**: Kling AI 2.1 (facial detail, lip-sync)
- **Wide/Establishing**: Google Veo 3 or Sora 2 (physics, scale)
- **Action Sequences**: Google Veo 3 (motion coherence)
- **VFX/Effects**: Runway Gen-4 (multi-scene, stylization)

### 4. Research Agent Automation (from Perplexity)

**Discovery Pipeline:**
- **Web Scraping**: AI blogs, documentation sites (hourly)
- **GitHub Monitoring**: Trending repos, new releases (daily)
- **API Marketplaces**: RapidAPI, Postman Network (daily)
- **Social Listening**: Twitter/X, Reddit, Hacker News (real-time)

**Benchmarking System:**
- **Standardized Test Prompts**: "A cat on a motorcycle at night"
- **Objective Metrics**: Latency, CLIP score, SSIM, FVD, cost
- **Subjective Metrics**: Human evaluation via Mechanical Turk
- **Success Rate**: Error tracking, reliability scoring

**SOTA Tracking:**
- **arXiv Monitoring**: Papers on video generation (daily)
- **GitHub Trending**: New implementations, fine-tuned models (daily)
- **Community Forums**: Reddit, Hugging Face discussions (real-time)
- **Leaderboards**: Track benchmark rankings and model releases

**Auto-Update Logic:**
```python
async def research_agent_loop():
    while True:
        # Discovery (every 6 hours)
        new_apis = await discover_apis()
        await catalog_new_apis(new_apis)
        
        # Benchmarking (every 12 hours)
        pending = await get_pending_benchmarks()
        results = await run_benchmark_suite(pending)
        await store_results(results)
        
        # SOTA tracking (daily)
        papers = await fetch_arxiv_papers("video generation")
        techniques = await extract_techniques(papers)
        await update_sota_database(techniques)
        
        # Recalculate rankings
        await recalculate_tool_rankings()
        await notify_on_changes()
        
        await asyncio.sleep(3600)  # 1 hour
```

---

## Implementation Summary

### Phase 1: ScriptSmith Enhancement (Week 1)
**Goal**: Generate ALT beats with complete metadata

**Key Changes:**
- Update system prompt with ALT beats methodology
- Add `generate_alt_beats(vrd, clarifications)` tool
- Add `ask_clarifying_questions(vrd)` tool
- Implement dual output (JSON + narrative)
- Apply 8-part story structure to timing

**Success Criteria:**
- ✅ Generates valid ALT beats JSON
- ✅ Asks 5 clarifying questions
- ✅ Timing within ±5s of VRD
- ✅ Complete metadata per beat

### Phase 2: ShotMaster Creation (Week 2)
**Goal**: Convert ALT beats to detailed shot specifications

**Implementation:**
- Create new agent in `sub_agents.py`
- Tools: `generate_shot_list()`, `determine_shot_type()`, `design_lighting()`
- Build shot library templates
- Generate storyboard descriptions

**Success Criteria:**
- ✅ Converts beats to 30+ shots
- ✅ Detailed specifications per shot
- ✅ Storyboard descriptions
- ✅ Visual continuity maintained

### Phase 3: VideoSolver Creation (Week 3)
**Goal**: Select optimal AI tools for each shot

**Implementation:**
- Create tool selection agent
- Query Tool Stack database
- Implement decision matrix (quality/cost/speed)
- Calculate complete workflows

**Success Criteria:**
- ✅ Selects optimal tool per shot
- ✅ Defines step-by-step workflow
- ✅ Accurate cost/time estimates
- ✅ Alternative options provided

### Phase 4: Deep Research Agent (Week 4)
**Goal**: Autonomous tool discovery and benchmarking

**Implementation:**
- Create `research_agent.py`
- Build discovery pipeline
- Implement benchmarking system
- Create SOTA tracker
- Add auto-update automation

**Success Criteria:**
- ✅ Discovers 5+ APIs per week
- ✅ Benchmarks all major tools
- ✅ Updates Tool Stack daily
- ✅ Notifies on SOTA changes

### Phase 5: Integration (Week 5)
**Goal**: Connect all agents with APIs

**Implementation:**
- Create orchestrator in `supervisor.py`
- Build REST endpoints
- Implement SSE streaming
- Add validation middleware

**Success Criteria:**
- ✅ Full pipeline works end-to-end
- ✅ Each agent < 30s response
- ✅ Streaming updates real-time
- ✅ Error handling robust

### Phase 6: Testing (Week 6)
**Goal**: Comprehensive validation

**Implementation:**
- Unit tests (>80% coverage)
- Integration tests
- Performance benchmarks
- Documentation

**Success Criteria:**
- ✅ All tests pass
- ✅ Performance benchmarks met
- ✅ Complete documentation
- ✅ Example workflows validated

---

## Data Structures

### VRD Input
```typescript
interface VRD {
  vrd_id: string;
  project_name: string;
  purpose: { objective: string };
  audience: { demographics: string[]; pain_points: string[] };
  key_messages: { core_message: string; supporting_messages: string[] };
  content_structure: { total_duration_seconds: number };
  style: { tone: string; mood: string; visual_style: string };
}
```

### ALT Beat Output
```typescript
interface ALTBeat {
  beat_id: string;
  timecode_start: string;
  duration_seconds: number;
  story_question: string;
  story_answer: string;
  script: { action: string; dialogue?: string };
  visual_requirements: { shot_type: string; lighting: string };
  audio_requirements: { dialogue_present: boolean; sound_effects: string[] };
  emotional_context: { character_emotion: string; intensity: number };
  narrative_function: { eight_part_position: string };
}
```

### Shot List Output
```typescript
interface Shot {
  shot_id: string;
  beat_ref: string;
  shot_type: string;
  camera_movement: string;
  duration_seconds: number;
  lighting: { time_of_day: string; mood: string };
  technical_complexity: { complexity_score: number; requires_vfx: boolean };
  storyboard_frame: { description: string; reference_image_prompt: string };
}
```

### Production Plan Output
```typescript
interface ProductionPlan {
  production_plan_id: string;
  total_cost_usd: number;
  total_time_minutes: number;
  shot_plans: Array<{
    shot_id: string;
    recommended_workflow: {
      steps: Array<{ tool: string; purpose: string; cost_usd: number }>;
      total_cost: number;
      quality_score: number;
    };
    alternative_workflows: Array<any>;
  }>;
}
```

---

## API Endpoints

### POST /api/production/script
Generate script with ALT beats from VRD
```json
Request: { "vrd": {}, "clarifications": {} }
Response: { "script_id": "", "beats": [], "metadata": {} }
```

### POST /api/production/shots
Generate shot list from ALT beats
```json
Request: { "script_id": "", "beats": [] }
Response: { "shot_list_id": "", "shots": [], "asset_summary": {} }
```

### POST /api/production/plan
Generate production plan from shots
```json
Request: { "shot_list_id": "", "shots": [], "constraints": {} }
Response: { "production_plan_id": "", "shot_plans": [], "cost_breakdown": {} }
```

### GET /api/research/tools
Query Tool Stack database
```json
Response: { "tools": [], "updated_at": "" }
```

---

## Tool Stack Database Schema

```sql
CREATE TABLE tools (
  tool_id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  category VARCHAR NOT NULL,  -- 'text_to_video', 'image_to_video', etc.
  capabilities JSONB,          -- max_resolution, max_duration, features
  quality_metrics JSONB,       -- quality_score, benchmark_score, sota_score
  pricing JSONB,               -- cost_per_second, billing_rate
  performance JSONB,           -- avg_generation_time, success_rate
  api_integration JSONB,       -- api_url, auth_method, sdk_available
  best_for TEXT[],             -- use cases
  limitations TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE benchmarks (
  benchmark_id VARCHAR PRIMARY KEY,
  tool_id VARCHAR REFERENCES tools(tool_id),
  test_prompt TEXT,
  latency_seconds FLOAT,
  quality_score FLOAT,
  cost_usd FLOAT,
  success_rate FLOAT,
  tested_at TIMESTAMP
);

CREATE TABLE workflows (
  workflow_id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  steps JSONB,                 -- array of tool steps
  use_cases TEXT[],
  avg_quality_score FLOAT,
  avg_cost_usd FLOAT,
  created_at TIMESTAMP
);
```

---

## Next Steps

1. **Review Documentation** → Read all created markdown files
2. **Study Research** → Review Perplexity findings above
3. **Start Week 1** → Enhance ScriptSmith in `sub_agents.py`
4. **Test Pipeline** → Run with example VRD
5. **Iterate** → Refine based on results

---

## Files Created

1. `/PokerCats/apps/agents/ALT_BEATS_SPEC.md` - Beat specification
2. `/PokerCats/apps/agents/IMPLEMENTATION_PLAN.md` - 6-week roadmap
3. `/PokerCats/apps/agents/QUICK_START_GUIDE.md` - Quick start guide
4. `/PokerCats/apps/agents/MULTI_AGENT_SYSTEM_OVERVIEW.md` - This file
5. `/PokerCats/apps/agents/scriptsmith.md` (v2.0) - Enhanced knowledge base

---

**Research Complete. Planning Complete. Ready to Build.** 🚀
