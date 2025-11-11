# Legacy Agents Analysis - Critical Findings

**Date**: November 6, 2025  
**Status**: ⚠️ **ISSUES FOUND - Action Required**  

---

## Executive Summary

The legacy agents in `sub_agents.py` serve **TWO critical purposes**:
1. ✅ **VRD implementation** (NO modular equivalent exists)
2. ⚠️ **Fallback agents** (PARTIALLY BROKEN)

**Critical Issue**: Legacy ScriptSmith agent references **undefined tools** and will **fail** if enhanced agents are unavailable.

---

## Detailed Analysis

### Purpose 1: VRD Implementation ✅ ESSENTIAL

**Functions**:
- `analyze_requirements(user_input)` - Keyword-based VRD extraction
- `define_video_scope(requirements)` - VRD document formatting

**Status**: **KEEP - No modular alternative exists**

**Current Usage**:
```python
# Enhanced VRD agent IMPORTS these legacy tools
# File: enhanced_sub_agents.py, Line 56
from .sub_agents import analyze_requirements, define_video_scope

@tool
def analyze_video_requirements(user_input: str) -> str:
    requirements = analyze_requirements(user_input)  # Legacy
    vrd = define_video_scope(requirements)           # Legacy
    return vrd
```

**Why No Modular Version?**:
- Modular tools directory has:
  - `alt_beat_generator.py` (script generation)
  - `shot_planner.py` (shot planning)
  - `tool_selector.py` (production planning)
  - `clarifying_questions.py` (HITL questions)
- But **NO** `vrd_analyzer.py` or equivalent

**Recommendation**: VRD functions should stay in `sub_agents.py` OR be moved to `tools/vrd_analyzer.py`

---

### Purpose 2: Fallback Agent Creators ⚠️ PARTIALLY BROKEN

**Agent Creators**:
```python
# File: sub_agents.py
def create_vrd_agent(model)         # Line 127 ✅ Works
def create_script_smith_agent(model) # Line 507 ❌ BROKEN
def create_shot_master_agent(model)  # Line 738 ✅ Works
def create_video_solver_agent(model) # Line 904 ✅ Works
```

**Fallback Mechanism** (supervisor.py):
```python
try:
    from .enhanced_sub_agents import (
        create_enhanced_vrd_agent,
        create_enhanced_script_smith_agent,
        ...
    )
    ENHANCED_AGENTS_AVAILABLE = True
except ImportError:
    # Falls back to legacy agents
    from .sub_agents import (
        create_vrd_agent,
        create_script_smith_agent,  # ❌ This will fail!
        ...
    )
    ENHANCED_AGENTS_AVAILABLE = False
```

---

## Critical Bug: ScriptSmith Fallback Broken

**File**: `sub_agents.py`, Line 507-513

**Code**:
```python
def create_script_smith_agent(model: BaseChatModel):
    tools = [generate_script, refine_dialogue]  # ❌ UNDEFINED!
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="script_smith_agent",
        ...
    )
```

**Problem**: Functions `generate_script` and `refine_dialogue` **DO NOT EXIST** in the file!

**Search Results**:
```bash
$ grep "def generate_script" sub_agents.py
# No results found

$ grep "def refine_dialogue" sub_agents.py  
# No results found
```

**Impact**: If enhanced agents are unavailable (e.g., Pydantic not installed), the fallback will **crash** when trying to create ScriptSmith.

**Error**:
```python
NameError: name 'generate_script' is not defined
```

---

## Function Duplication Analysis

### ScriptSmith Functions

| Function | Legacy (sub_agents.py) | Modular (tools/) | Status |
|----------|------------------------|------------------|--------|
| `generate_alt_beats()` | ✅ Line 308 (simple) | ✅ alt_beat_generator.py | DUPLICATED |
| `ask_clarifying_questions()` | ✅ Line 424 (simple) | ✅ clarifying_questions.py | DUPLICATED |
| `validate_alt_beats_timing()` | ✅ Line 473 | ✅ clarifying_questions.py | DUPLICATED |

**Analysis**: Legacy versions are **placeholder implementations** superseded by proper modular tools.

---

### ShotMaster Functions

| Function | Legacy (sub_agents.py) | Modular (tools/) | Status |
|----------|------------------------|------------------|--------|
| `design_storyboard()` | ✅ Line 661 (placeholder) | ✅ shot_planner.py | DUPLICATED |
| `suggest_shot_composition()` | ✅ Line 704 (placeholder) | ✅ shot_planner.py | DUPLICATED |

**Analysis**: Legacy versions return **template strings**, not real shot planning.

---

### VideoSolver Functions

| Function | Legacy (sub_agents.py) | Modular (tools/) | Status |
|----------|------------------------|------------------|--------|
| `create_asset_list()` | ✅ Line 783 (placeholder) | ✅ tool_selector.py | DUPLICATED |
| `generate_timeline()` | ✅ Line 818 (placeholder) | ✅ tool_selector.py | DUPLICATED |
| `suggest_editing_workflow()` | ✅ Line 858 (placeholder) | ✅ tool_selector.py | DUPLICATED |

**Analysis**: Legacy versions return **hardcoded templates**, not SOTA tool selection.

---

## What Should Be Kept vs Removed?

### ✅ KEEP (Essential)

1. **VRD Functions** (NO modular equivalent):
   - `analyze_requirements()` - Line 16
   - `define_video_scope()` - Line 57
   - `create_vrd_agent()` - Line 127

2. **Fallback Agent Creators** (needed when modular tools unavailable):
   - `create_vrd_agent()` - Line 127
   - `create_shot_master_agent()` - Line 738 ✅ Works
   - `create_video_solver_agent()` - Line 904 ✅ Works
   - `create_script_smith_agent()` - Line 507 ❌ Must be fixed

---

### ❌ CAN REMOVE (Obsolete duplicates)

**ScriptSmith Functions** (superseded by modular tools):
- `generate_alt_beats()` - Line 308-421 (112 lines)
- `ask_clarifying_questions()` - Line 424-470 (46 lines)
- `validate_alt_beats_timing()` - Line 473-504 (31 lines)

**ShotMaster Functions** (superseded by modular tools):
- `design_storyboard()` - Line 661-701 (40 lines)
- `suggest_shot_composition()` - Line 704-735 (31 lines)

**VideoSolver Functions** (superseded by modular tools):
- `create_asset_list()` - Line 783-815 (32 lines)
- `generate_timeline()` - Line 818-855 (37 lines)
- `suggest_editing_workflow()` - Line 858-901 (43 lines)

**Total removable**: ~372 lines of obsolete code

---

## Recommended Actions

### Option 1: Minimal Fix (Immediate) ✅ RECOMMENDED

**Fix the broken ScriptSmith fallback**:

```python
# File: sub_agents.py, Line 507-513
def create_script_smith_agent(model: BaseChatModel):
    """Create ScriptSmith agent with legacy tools"""
    tools = [
        generate_alt_beats,          # Use legacy version
        ask_clarifying_questions,     # Use legacy version
        validate_alt_beats_timing     # Use legacy version
    ]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="script_smith_agent",
        prompt="""..."""
    )
```

**Impact**:
- ✅ Fallback system works correctly
- ✅ No functionality loss
- ⚠️ Keeps duplicate code

---

### Option 2: Aggressive Cleanup (Future Sprint)

**Steps**:

1. **Create modular VRD tools**:
   ```
   tools/vrd_analyzer.py
   ├── analyze_requirements()
   ├── define_video_scope()
   └── extract_vrd_from_llm()
   ```

2. **Remove obsolete functions** from `sub_agents.py`:
   - All ScriptSmith, ShotMaster, VideoSolver implementation functions
   - Keep only agent creators

3. **Update fallback agent creators** to use modular tools with try-except:
   ```python
   def create_script_smith_agent(model):
       try:
           from tools import generate_alt_beats
           tools = [generate_alt_beats, ...]
       except ImportError:
           # Ultra-minimal fallback
           tools = []
       ...
   ```

4. **Result**: `sub_agents.py` becomes **thin wrapper** only:
   - VRD functions (if not moved to tools/)
   - Agent creators that import from tools/

**Impact**:
- ✅ Eliminates 372 lines of duplicate code
- ✅ Single source of truth for each function
- ⚠️ Requires more refactoring

---

### Option 3: Keep Current Design (Do Nothing)

**Rationale**:
- Legacy code serves as **documentation** of original design
- Provides **fallback** when modular tools unavailable
- **"Works on my machine"** philosophy

**Impact**:
- ❌ Broken ScriptSmith fallback remains
- ❌ Duplicate code maintenance burden
- ❌ Confusion for future developers

**Status**: **NOT RECOMMENDED**

---

## Architecture Diagram

### Current State (With Issues)

```
supervisor.py
    ├── Try: Import enhanced_sub_agents
    │   ├── create_enhanced_vrd_agent()
    │   │   └── imports legacy: analyze_requirements ✅
    │   ├── create_enhanced_script_smith_agent()
    │   │   └── uses tools/alt_beat_generator.py ✅
    │   ├── create_enhanced_shot_master_agent()
    │   │   └── uses tools/shot_planner.py ✅
    │   └── create_enhanced_video_solver_agent()
    │       └── uses tools/tool_selector.py ✅
    │
    └── Except: Fallback to sub_agents (legacy)
        ├── create_vrd_agent() ✅ Works
        ├── create_script_smith_agent() ❌ BROKEN
        │   └── tools = [generate_script, refine_dialogue]
        │       └── NameError: undefined
        ├── create_shot_master_agent() ✅ Works
        │   └── tools = [design_storyboard, suggest_shot_composition]
        └── create_video_solver_agent() ✅ Works
            └── tools = [create_asset_list, generate_timeline, ...]
```

---

## Immediate Action Required

### Fix Priority: 🔴 HIGH

**File**: `agents/sub_agents.py`  
**Lines**: 507-513  
**Issue**: Undefined tools in ScriptSmith fallback  

**Quick Fix**:
```python
def create_script_smith_agent(model: BaseChatModel):
    tools = [
        generate_alt_beats,           # Defined at line 308
        ask_clarifying_questions,      # Defined at line 424
        validate_alt_beats_timing      # Defined at line 473
    ]
    # ... rest of function
```

**Test**:
```python
# Simulate enhanced agents unavailable
import sys
sys.modules['tools'] = None

from agents.sub_agents import create_script_smith_agent
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
agent = create_script_smith_agent(model)  # Should work, not crash

print("✅ Fallback ScriptSmith works!")
```

---

## Long-term Recommendations

1. **Sprint 3.1**: Fix immediate ScriptSmith bug (Option 1)
2. **Sprint 3.2**: Create modular VRD tools (`tools/vrd_analyzer.py`)
3. **Sprint 4**: Remove obsolete duplicate functions (Option 2)
4. **Sprint 4**: Add comprehensive fallback tests

---

## Conclusion

**Legacy agents are NOT orphaned** - they serve critical purposes:

1. ✅ **VRD implementation** - Used by enhanced agents, NO replacement exists
2. ⚠️ **Fallback system** - Needed when modular tools unavailable, but ScriptSmith is **broken**

**Immediate Action**: Fix ScriptSmith fallback by updating tool references.

**Future Work**: Eliminate duplicate code by creating modular VRD tools and cleaning up obsolete functions.

---

**Status**: Analysis complete, fix ready to implement.
