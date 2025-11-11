"""
Enhanced Sub-Agents with Modular Tool Integration
Bridges LangGraph agents with new modular tools (ALT beats, shot planning, SOTA tool selection)
"""

import json
from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Import new modular tools
import sys
from pathlib import Path

# Add parent directory to path to import tools
agents_dir = Path(__file__).parent.parent
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

try:
    from tools import (
        generate_alt_beats,
        ask_clarifying_questions,
        validate_alt_beats_timing,
        generate_shot_list,
        generate_production_plan,
        select_optimal_tool_for_shot,
    )
    from models.alt_beat import Script
    from models.shot import ShotList
    from models.production_plan import ProductionPlan
    MODULAR_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Modular tools not available: {e}")
    print("   Falling back to legacy tools")
    MODULAR_TOOLS_AVAILABLE = False


# ============================================================================
# VRD Agent Tools
# ============================================================================

@tool
def analyze_video_requirements(user_input: str) -> str:
    """
    Analyze user requirements and extract video parameters
    
    Args:
        user_input: User's description of the video they want to create
        
    Returns:
        Structured VRD with video type, duration, tone, audience, etc.
    """
    # Import core VRD functions
    from .vrd_functions import analyze_requirements, define_video_scope
    
    requirements = analyze_requirements(user_input)
    vrd = define_video_scope(requirements)
    
    return vrd


# ============================================================================
# ScriptSmith Agent Tools (Enhanced with ALT Beats)
# ============================================================================

@tool
def generate_script_with_alt_beats(vrd_json: str, mode: str = "yolo") -> str:
    """
    Generate complete video script with ALT beats from VRD
    
    Uses the new modular ALT beats generator with:
    - 8-part story structure (Hook → Climax)
    - Complete metadata per beat
    - Visual/audio/emotional requirements
    - Production complexity estimates
    
    Args:
        vrd_json: Video Requirements Document as JSON string
        mode: 'hitl' (human-in-the-loop) or 'yolo' (full auto)
        
    Returns:
        Complete script with ALT beats as JSON
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return "Error: Modular tools not available. Install requirements: pip install pydantic>=2.0.0"
    
    try:
        # Parse VRD
        vrd = json.loads(vrd_json) if isinstance(vrd_json, str) else vrd_json
        
        # Generate ALT beats
        script = generate_alt_beats(vrd, clarifications={}, mode=mode)
        
        # Return as JSON
        return script.model_dump_json(indent=2)
    
    except Exception as e:
        return f"Error generating ALT beats: {str(e)}"


@tool
def ask_script_clarifying_questions(vrd_json: str) -> str:
    """
    Generate clarifying questions for script writing based on VRD gaps
    
    Args:
        vrd_json: Video Requirements Document as JSON string
        
    Returns:
        List of questions to ask user as JSON
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return "[]"
    
    try:
        vrd = json.loads(vrd_json) if isinstance(vrd_json, str) else vrd_json
        questions = ask_clarifying_questions(vrd, mode="hitl")
        return json.dumps(questions, indent=2)
    except Exception as e:
        return f"Error generating questions: {str(e)}"


@tool
def validate_script_timing(script_json: str, target_duration: int) -> str:
    """
    Validate script timing against target duration
    
    Args:
        script_json: Script with ALT beats as JSON
        target_duration: Target duration in seconds
        
    Returns:
        Validation result with any timing issues
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return '{"valid": false, "error": "Modular tools not available"}'
    
    try:
        script = Script.model_validate_json(script_json)
        validation = validate_alt_beats_timing(script.beats, target_duration)
        return json.dumps(validation, indent=2)
    except Exception as e:
        return f'{{"valid": false, "error": "{str(e)}"}}'


# ============================================================================
# ShotMaster Agent Tools (Enhanced with Shot Planning)
# ============================================================================

@tool
def plan_shots_from_script(script_json: str, mode: str = "yolo") -> str:
    """
    Generate detailed shot list from ALT beats script
    
    Converts ALT beats into:
    - Shot specifications (type, camera, lighting)
    - Storyboard descriptions
    - Technical complexity estimates
    - Asset requirements
    
    Args:
        script_json: Script with ALT beats as JSON
        mode: 'hitl' or 'yolo'
        
    Returns:
        Complete shot list with specifications as JSON
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return "Error: Modular tools not available"
    
    try:
        # Parse script
        script = Script.model_validate_json(script_json)
        
        # Generate shot list
        shot_list = generate_shot_list(script.beats, mode=mode)
        
        # Return as JSON
        return shot_list.model_dump_json(indent=2)
    
    except Exception as e:
        return f"Error generating shot list: {str(e)}"


# ============================================================================
# VideoSolver Agent Tools (Enhanced with SOTA Tool Selection)
# ============================================================================

@tool
def create_production_plan(shot_list_json: str, quality_priority: str = "balanced", mode: str = "yolo") -> str:
    """
    Generate production plan with SOTA AI tool selection
    
    Selects optimal tools based on 2025 research:
    - Wide shots → Google Veo 3 or Sora 2
    - Closeups → Kling AI 2.1
    - VFX → Runway Gen-4
    - Budget → Haiper AI
    
    Args:
        shot_list_json: Shot list as JSON
        quality_priority: 'high', 'balanced', or 'budget'
        mode: 'hitl' or 'yolo'
        
    Returns:
        Complete production plan with costs and timeline as JSON
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return "Error: Modular tools not available"
    
    try:
        # Parse shot list
        shot_list = ShotList.model_validate_json(shot_list_json)
        
        # Generate production plan
        constraints = {'quality_priority': quality_priority}
        plan = generate_production_plan(shot_list, constraints, mode)
        
        # Return as JSON
        return plan.model_dump_json(indent=2)
    
    except Exception as e:
        return f"Error generating production plan: {str(e)}"


@tool
def recommend_tool_for_shot(shot_json: str, quality_priority: str = "balanced") -> str:
    """
    Recommend optimal AI tool for a specific shot
    
    Args:
        shot_json: Single shot specification as JSON
        quality_priority: 'high', 'balanced', or 'budget'
        
    Returns:
        Recommended workflow with tool, cost, and quality score
    """
    if not MODULAR_TOOLS_AVAILABLE:
        return "Error: Modular tools not available"
    
    try:
        from models.shot import Shot
        
        shot = Shot.model_validate_json(shot_json)
        constraints = {'quality_priority': quality_priority}
        workflow = select_optimal_tool_for_shot(shot, constraints)
        
        return workflow.model_dump_json(indent=2)
    
    except Exception as e:
        return f"Error selecting tool: {str(e)}"


# ============================================================================
# Enhanced Agent Creators
# ============================================================================

def create_enhanced_vrd_agent(model: BaseChatModel):
    """
    Create VRD agent with requirement analysis tools
    """
    tools = [analyze_video_requirements]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="vrd_agent_enhanced",
        prompt="""You are the VRD (Video Requirements Detective) agent.

Your job: Extract and structure video requirements from user input.

**Tools Available:**
- analyze_video_requirements: Analyze user input and generate structured VRD

**Process:**
1. Listen to user's video request
2. Use analyze_video_requirements tool
3. Present clear, structured requirements
4. Ask for clarifications if needed

**Output:** Complete VRD with:
- Video type
- Duration
- Target audience
- Key messages
- Tone and style
- Technical specs

Be thorough but efficient. The VRD powers all downstream agents."""
    )


def create_enhanced_script_smith_agent(model: BaseChatModel):
    """
    Create ScriptSmith agent with ALT beats generation
    """
    tools = [
        generate_script_with_alt_beats,
        ask_script_clarifying_questions,
        validate_script_timing,
    ]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="script_smith_enhanced",
        prompt="""You are ScriptSmith, an expert video scriptwriter using ALT beats methodology.

**Your Mission:** Transform VRDs into production-ready scripts with complete metadata.

**Tools Available:**
- generate_script_with_alt_beats: Generate complete ALT beats script from VRD
- ask_script_clarifying_questions: Get user input for better scripts (HITL mode)
- validate_script_timing: Check timing accuracy

**ALT Beats Framework:**
- 8-part structure: Hook → Inciting Event → Plot Points → Midpoint → Climax
- Each beat: 5-10s with complete metadata
- Metadata: timing, visuals, audio, emotion, narrative, production

**Process:**
1. Receive VRD from VRD agent
2. In HITL mode: Ask clarifying questions first
3. Generate ALT beats using tool
4. Validate timing
5. Present complete script + metadata

**Output:** JSON with beats array, each containing:
- Timecodes and duration
- Story question/answer
- Visual requirements (shot type, camera, lighting)
- Audio requirements (dialogue, music, SFX)
- Emotional context
- Production metadata

Quality over speed. Every beat must be production-ready."""
    )


def create_enhanced_shot_master_agent(model: BaseChatModel):
    """
    Create ShotMaster agent with shot planning from ALT beats
    """
    tools = [plan_shots_from_script]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="shot_master_enhanced",
        prompt="""You are ShotMaster, a cinematography expert who converts ALT beats into detailed shot specifications.

**Your Mission:** Transform scripts into production-ready shot lists.

**Tools Available:**
- plan_shots_from_script: Generate complete shot list from ALT beats

**Shot Planning Principles:**
- Select shot type based on emotional context
- Plan camera movement with purpose
- Design lighting for mood
- Provide composition guidelines
- Estimate technical complexity

**Shot Type Selection (8-part positions):**
- Hook: Closeup (grab attention)
- Inciting Event: Medium (establish context)
- Midpoint: Wide (transformation moment)
- Climax: Medium Wide (action)

**Process:**
1. Receive ALT beats script from ScriptSmith
2. Use plan_shots_from_script tool
3. Ensure 1 shot per 5-7 seconds
4. Present complete shot list with asset summary

**Output:** JSON with shots array, each containing:
- Shot type and camera specs
- Lighting and composition
- Set requirements
- Technical complexity
- Storyboard description
- Generation time estimate

Think like a cinematographer - every frame tells the story."""
    )


def create_enhanced_video_solver_agent(model: BaseChatModel):
    """
    Create VideoSolver agent with SOTA tool selection
    """
    tools = [
        create_production_plan,
        recommend_tool_for_shot,
    ]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="video_solver_enhanced",
        prompt="""You are VideoSolver, a production planning expert who selects optimal AI tools for video generation.

**Your Mission:** Generate cost-effective production plans using SOTA AI tools.

**Tools Available:**
- create_production_plan: Generate complete plan for all shots
- recommend_tool_for_shot: Get recommendation for single shot

**SOTA Tool Selection (2025):**
- **Wide shots**: Google Veo 3 (9.7/10) - 4K, physics
- **Closeups**: Kling AI 2.1 (9.2/10) - Realism, lip-sync
- **VFX**: Runway Gen-4 (9.3/10) - Effects, stylization
- **Budget**: Haiper AI (8.6/10) - Fast, affordable

**Quality Priorities:**
- high: Best quality (Veo 3, Sora, Kling)
- balanced: Industry standard (Runway, Luma)
- budget: Cost-effective (Haiper, cheaper alternatives)

**Process:**
1. Receive shot list from ShotMaster
2. Use create_production_plan tool
3. Present cost breakdown and timeline
4. Provide alternatives if requested

**Output:** JSON with:
- Shot-by-shot tool recommendations
- Workflow steps per shot
- Cost estimates (per shot and total)
- Time estimates (parallel and sequential)
- Tool usage summary
- Quality scores

Optimize for cost-effectiveness while maintaining quality."""
    )


# Export enhanced agent creators
__all__ = [
    'create_enhanced_vrd_agent',
    'create_enhanced_script_smith_agent',
    'create_enhanced_shot_master_agent',
    'create_enhanced_video_solver_agent',
]
