"""
LangGraph Supervisor Agent
Orchestrates specialized sub-agents for video editing tasks
"""

import os
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
# NOTE: langgraph_supervisor is deprecated - implementing supervisor pattern directly
# from langgraph_supervisor import create_supervisor

# Import model factory for Gemini/OpenAI selection
from .model_factory import get_agent_model, Provider
from typing import List, Callable, Any, Dict
from copy import deepcopy

# Import observability for tracking degraded mode
from .observability import (
    get_observability,
    AgentMode,
    DegradationReason,
    logger,
)

# Try to import enhanced agents, fallback to legacy if not available
try:
    from .enhanced_sub_agents import (
        create_enhanced_vrd_agent,
        create_enhanced_script_smith_agent,
        create_enhanced_shot_master_agent,
        create_enhanced_video_solver_agent,
    )
    ENHANCED_AGENTS_AVAILABLE = True
    logger.info("✅ Enhanced agents loaded - optimal mode active")
    get_observability().log_mode_change(
        AgentMode.OPTIMAL,
        "supervisor",
        details={"agents": "enhanced"}
    )
except ImportError as e:
    logger.warning(
        f"⚠️  Enhanced agents not available: {e}",
        extra={
            "component": "supervisor",
            "mode": "degraded",
            "degradation_reason": DegradationReason.IMPORT_ERROR.value,
        }
    )
    print(f"⚠️  Enhanced agents not available: {e}")
    print("   Falling back to legacy agents")
    
    from .sub_agents import (
        create_vrd_agent,
        create_script_smith_agent,
        create_shot_master_agent,
        create_video_solver_agent,
    )
    ENHANCED_AGENTS_AVAILABLE = False
    
    # Log degradation
    get_observability().log_mode_change(
        AgentMode.DEGRADED,
        "supervisor",
        DegradationReason.IMPORT_ERROR,
        {
            "error": str(e),
            "fallback": "legacy_agents",
            "impact": "reduced_functionality"
        }
    )
    
    # Print user-facing warning
    get_observability().print_degradation_warning()


def create_supervisor(
    agents: List[Callable],
    model: Any,
    state_schema: type,
    prompt: str,
    parallel_tool_calls: bool = False,
    output_mode: str = "full_history",
    include_agent_name: str = "inline"
):
    """
    Create a supervisor workflow using StateGraph directly.
    Implements supervisor pattern without deprecated langgraph_supervisor package.
    
    Args:
        agents: List of agent callables
        model: LLM model for supervisor decisions
        state_schema: State type definition
        prompt: System prompt for supervisor
        parallel_tool_calls: Whether to allow parallel agent calls
        output_mode: How to handle output messages
        include_agent_name: Whether to tag messages with agent names
        
    Returns:
        Compiled StateGraph workflow
    """
    
    def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervisor decides which agent should handle the request"""
        import re
        
        messages = state.get("messages", [])
        iterations = state.get("iterations", 0)
        
        # Prevent infinite loops - max 5 iterations
        if iterations >= 5:
            logger.warning("Max iterations reached, ending workflow")
            return {**state, "next_agent": -1, "iterations": iterations}
        
        # Check if we have a recent agent response - if so, likely done
        if len(messages) > 2:
            last_msg = messages[-1]
            if isinstance(last_msg, AIMessage) and len(last_msg.content) > 50:
                # Agent gave substantive response, end workflow
                return {**state, "next_agent": -1, "iterations": iterations}
        
        # Build proper message list for Gemini
        lc_messages = []
        
        # STRICT system prompt for structured output
        sys_content = f"{prompt}\n\n" \
                      "**CRITICAL**: You MUST respond in EXACTLY this format:\n" \
                      "- To route to an agent: 'AGENT: <number>' (e.g., 'AGENT: 0')\n" \
                      "- To finish: 'END'\n" \
                      "Do NOT include any other text. Just 'AGENT: X' or 'END'."
        lc_messages.append(SystemMessage(content=sys_content))
        
        # Add conversation messages
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                lc_messages.append(msg)
        
        if not any(isinstance(m, HumanMessage) for m in lc_messages):
            lc_messages.append(HumanMessage(content="Process this request."))
        
        # Get supervisor decision
        response = model.invoke(lc_messages)
        content = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"Supervisor decision: {content}")
        
        # Parse with regex for robust extraction
        if "END" in content.upper():
            return {**state, "next_agent": -1, "iterations": iterations}
        
        # Look for "AGENT: N" pattern
        match = re.search(r'AGENT:\s*(\d+)', content, re.IGNORECASE)
        if match:
            agent_idx = int(match.group(1))
            if 0 <= agent_idx < len(agents):
                return {**state, "next_agent": agent_idx, "iterations": iterations + 1}
        
        # Fallback: if first message, route to agent 0, otherwise END
        if iterations == 0:
            logger.warning(f"Could not parse supervisor response: {content}. Starting with agent 0.")
            return {**state, "next_agent": 0, "iterations": 1}
        else:
            logger.warning(f"Could not parse supervisor response: {content}. Ending workflow.")
            return {**state, "next_agent": -1, "iterations": iterations}
    
    # Create agent wrapper nodes
    agent_nodes = {}
    for idx, agent in enumerate(agents):
        def make_agent_node(agent_fn, agent_idx):
            def node_fn(state):
                messages = list(state.get("messages", []))
                
                # Add agent identifier
                if include_agent_name == "inline":
                    messages.append(SystemMessage(content=f"[Agent {agent_idx} processing]"))
                
                # Call agent
                agent_state = {**state, "messages": messages}
                result = agent_fn.invoke(agent_state)
                
                # Merge results
                if output_mode == "full_history":
                    new_messages = messages + result.get("messages", [])
                else:
                    # Only keep last message from agent
                    last_msg = result.get("messages", [])[-1:] if result.get("messages") else []
                    new_messages = messages + last_msg
                
                return {**state, "messages": new_messages}
            
            return node_fn
        
        agent_nodes[f"agent_{idx}"] = make_agent_node(agent, idx)
    
    # Build graph
    graph = StateGraph(state_schema)
    graph.add_node("supervisor", supervisor_node)
    
    for agent_name, agent_fn in agent_nodes.items():
        graph.add_node(agent_name, agent_fn)
    
    # Add edges
    graph.add_edge(START, "supervisor")
    
    # Conditional routing from supervisor to agents
    def route_supervisor(state):
        next_agent = state.get("next_agent", 0)
        if next_agent == -1:
            return END
        return f"agent_{next_agent}"
    
    graph.add_conditional_edges("supervisor", route_supervisor)
    
    # Agents return to supervisor
    for agent_name in agent_nodes:
        graph.add_edge(agent_name, "supervisor")
    
    return graph


class SupervisorState(MessagesState):
    """
    Extended state for supervisor agent with additional context
    """
    task_type: str = "general"  # general, script, storyboard, production
    user_context: dict = {}
    assets_generated: list = []
    next_agent: int = 0  # For supervisor routing
    iterations: int = 0  # Track iterations to prevent infinite loops


def create_supervisor_workflow(provider: Provider = "google"):
    """
    Create the supervisor workflow with sub-agents
    
    Args:
        provider: Model provider ("google" or "openai")
        
    Returns:
        Compiled LangGraph workflow with checkpointing
    """
    # Get model provider preference from env or use parameter
    provider = os.getenv("MODEL_PROVIDER", provider).lower()
    
    # Initialize optimized LLMs for each agent using model factory
    supervisor_model = get_agent_model("supervisor", provider=provider)
    vrd_model = get_agent_model("vrd_agent", provider=provider)
    script_model = get_agent_model("script_smith_agent", provider=provider)
    shot_model = get_agent_model("shot_master_agent", provider=provider)
    solver_model = get_agent_model("video_solver_agent", provider=provider)
    
    # Create specialized sub-agents (enhanced if available)
    if ENHANCED_AGENTS_AVAILABLE:
        vrd_agent = create_enhanced_vrd_agent(vrd_model)
        script_smith_agent = create_enhanced_script_smith_agent(script_model)
        shot_master_agent = create_enhanced_shot_master_agent(shot_model)
        video_solver_agent = create_enhanced_video_solver_agent(solver_model)
        logger.info("Using enhanced agents (optimal mode)")
    else:
        # Using fallback agents - track for observability
        logger.warning("Using legacy fallback agents (degraded mode)")
        get_observability().log_fallback_triggered(
            agent_id="supervisor",
            fallback_strategy="legacy_agents",
            reason="enhanced_agents_unavailable",
            input_context={"provider": provider}
        )
        
        vrd_agent = create_vrd_agent(vrd_model)
        script_smith_agent = create_script_smith_agent(script_model)
        shot_master_agent = create_shot_master_agent(shot_model)
        video_solver_agent = create_video_solver_agent(solver_model)
    
    # Create supervisor with sub-agents
    supervisor = create_supervisor(
        agents=[
            vrd_agent,
            script_smith_agent,
            shot_master_agent,
            video_solver_agent,
        ],
        model=supervisor_model,
        state_schema=SupervisorState,
        prompt="""You are the OpenCut Video Production Supervisor.

Your role is to orchestrate specialized agents to help users create professional videos.
You manage four expert agents:

1. **VRD (Video Requirements Detective)**: Analyzes user requirements and defines project scope
   - Use for: Understanding what the user wants to create
   - Extracts: Video type, duration, style, target audience, key messages

2. **ScriptSmith**: Writes compelling video scripts and narratives
   - Use for: Creating scripts, voiceovers, dialogue
   - Delivers: Scene-by-scene scripts with timing and emotional beats

3. **ShotMaster**: Designs visual storyboards and shot compositions
   - Use for: Planning visual sequences, camera angles, compositions
   - Outputs: Detailed shot lists and storyboard descriptions

4. **VideoSolver**: Plans production logistics and technical requirements
   - Use for: Asset procurement, timeline planning, technical specs
   - Provides: Asset lists, timelines, editing instructions

**Workflow Strategy:**
- Start with VRD to understand requirements
- Route to ScriptSmith for narrative development
- Use ShotMaster for visual planning
- Coordinate VideoSolver for production planning
- You can delegate to multiple agents if tasks are independent

**Communication Style:**
- Be concise and action-oriented
- Coordinate between agents efficiently
- Present final deliverables clearly to the user
- Ask for clarification when requirements are ambiguous
""",
        parallel_tool_calls=False,  # Sequential execution for video workflow
        output_mode="full_history",  # Show all agent interactions
        include_agent_name="inline",  # Tag messages with agent names
    )
    
    # Compile with checkpointing for human-in-the-loop
    memory = MemorySaver()
    workflow = supervisor.compile(checkpointer=memory)
    
    return workflow


def create_simple_supervisor():
    """
    Create a simplified supervisor for general conversation
    Routes to specialized agents only when explicitly needed
    
    Returns:
        Basic supervisor workflow
    """
    # Use Gemini Flash for speed and better rate limits
    provider = os.getenv("MODEL_PROVIDER", "google").lower()
    model = get_agent_model("supervisor", provider=provider)
    
    class SimpleState(MessagesState):
        """Simple state for testing"""
        pass
    
    def supervisor_node(state: SimpleState):
        """Simple supervisor that responds directly"""
        raw_messages = state["messages"]
        
        # Build proper message list for Gemini
        lc_messages = []
        
        # Add system instruction
        lc_messages.append(
            SystemMessage(content="""You are a friendly AI assistant specializing in video production.

When users greet you or chat casually, respond naturally and warmly.
When users want to create videos, help them by:
- Understanding their video goals (type, duration, audience, message)
- Offering to help with scripts, storyboards, or production planning
- Asking clarifying questions to gather requirements

Be conversational, helpful, and concise. Don't overwhelm with technical jargon unless asked.""")
        )
        
        # Add conversation messages (already LangChain objects from execute.py)
        for msg in raw_messages:
            if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                lc_messages.append(msg)
        
        # Invoke model with proper messages
        response = model.invoke(lc_messages)
        return {"messages": [response]}
    
    # Build simple graph
    workflow = StateGraph(SimpleState)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("supervisor", END)
    
    # Compile with memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# Export compiled workflows
supervisor_workflow = None  # Will be initialized on first use


def get_supervisor_workflow():
    """
    Lazy initialization of supervisor workflow
    
    TEMPORARY: Using simple supervisor until multi-agent routing is refined
    """
    global supervisor_workflow
    
    if supervisor_workflow is None:
        # Use simple supervisor for now - multi-agent routing needs more work
        # Issue: Routes simple greetings like "hey" to specialized agents
        # TODO: Add intent classification before routing
        supervisor_workflow = create_simple_supervisor()
        print("✅ Using simple supervisor (single-agent mode)")
        
        # Uncomment when multi-agent routing is ready:
        # try:
        #     supervisor_workflow = create_supervisor_workflow()
        #     print("✅ Supervisor workflow initialized with all sub-agents")
        # except Exception as e:
        #     print(f"⚠️  Error initializing full supervisor: {e}")
        #     supervisor_workflow = create_simple_supervisor()
    
    return supervisor_workflow
