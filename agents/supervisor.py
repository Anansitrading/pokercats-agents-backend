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
    
    def conversational_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greetings and small talk without routing to specialized agents"""
        messages = list(state.get("messages", []))
        intent = state.get("intent", "unknown")
        
        lc_messages = []
        
        # Friendly conversational prompt
        sys_prompt = """You are a friendly AI assistant for video production.
The user just greeted you or made small talk. Respond warmly and naturally.
If appropriate, mention you can help with video creation (scripts, storyboards, planning).
Keep it brief and conversational."""
        
        lc_messages.append(SystemMessage(content=sys_prompt))
        
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage, SystemMessage)):
                lc_messages.append(msg)
        
        response = model.invoke(lc_messages)
        messages.append(response)
        
        return {**state, "messages": messages, "next_agent": -1}  # End after response
    
    def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervisor decides routing based on classified intent"""
        import re
        
        intent = state.get("intent", "unknown")
        iterations = state.get("iterations", 0)
        messages = state.get("messages", [])
        
        logger.info(f"Supervisor routing with intent: {intent}")
        
        # Prevent infinite loops
        if iterations >= 5:
            logger.warning("Max iterations reached, ending workflow")
            return {**state, "next_agent": -1, "iterations": iterations}
        
        # Handle based on intent
        if intent in ["greeting", "small_talk"]:
            # Route to conversational handler
            logger.info(f"Intent is {intent}, routing to conversational response")
            return {**state, "next_agent": -2}  # -2 signals conversational response
        
        elif intent == "mixed":
            # Handle greeting first, then prepare for video task
            logger.info("Mixed intent detected, handling conversationally")
            return {**state, "next_agent": -2}  # Respond to greeting, user can follow up
        
        elif intent == "video_request":
            # Route to appropriate video agent - for now default to VRD (agent 0)
            logger.info("Video request detected, routing to VRD agent")
            return {**state, "next_agent": 0, "iterations": iterations + 1}
        
        else:
            # Unknown intent - ask for clarification conversationally
            logger.warning(f"Unknown intent: {intent}, routing to conversational response")
            return {**state, "next_agent": -2}
    
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
    
    # Build graph with intent classification
    graph = StateGraph(state_schema)
    
    # Add all nodes
    graph.add_node("intent_classifier", create_intent_classifier_node(model))
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("conversational_response", conversational_response_node)
    
    for agent_name, agent_fn in agent_nodes.items():
        graph.add_node(agent_name, agent_fn)
    
    # Routing: START → intent_classifier → supervisor → conversational_response or agents
    graph.add_edge(START, "intent_classifier")
    graph.add_edge("intent_classifier", "supervisor")
    
    # Conditional routing from supervisor
    def route_supervisor(state):
        next_agent = state.get("next_agent", 0)
        if next_agent == -1:
            return END
        elif next_agent == -2:
            return "conversational_response"
        return f"agent_{next_agent}"
    
    graph.add_conditional_edges("supervisor", route_supervisor)
    
    # Conversational response ends workflow
    graph.add_edge("conversational_response", END)
    
    # Agents can either END or return to supervisor for multi-step workflows
    for agent_name in agent_nodes:
        graph.add_edge(agent_name, END)  # For now, agents end after responding
    
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
    intent: str = "unknown"  # Classified user intent
    intent_details: dict = {}  # Additional intent information


def create_intent_classifier_node(model: Any):
    """
    Create intent classifier node that categorizes user input
    
    Args:
        model: LLM model for intent classification
        
    Returns:
        Intent classifier function
    """
    def classify_intent(state: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user intent before routing to agents"""
        import json
        
        messages = state.get("messages", [])
        if not messages:
            return {**state, "intent": "unknown"}
        
        # Get the last user message
        last_user_msg = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_user_msg = msg.content
                break
        
        if not last_user_msg:
            return {**state, "intent": "unknown"}
        
        # Structured intent classification prompt
        intent_prompt = f"""Classify the user's intent. Respond ONLY with valid JSON in this exact format:
{{
  "intent": "<one of: greeting, small_talk, video_request, mixed, unknown>",
  "details": {{}},
  "confidence": "<high/medium/low>"
}}

Intent categories:
- "greeting": Simple greetings like "hi", "hey", "hello"
- "small_talk": Casual conversation, questions about the system, etc.
- "video_request": User wants to create/plan/discuss a video project
- "mixed": Contains both greeting AND video request
- "unknown": Unclear intent

Examples:
User: "hey" → {{"intent": "greeting", "details": {{}}, "confidence": "high"}}
User: "I want to make a video" → {{"intent": "video_request", "details": {{"topic": "unspecified"}}, "confidence": "high"}}
User: "Hey, can you help me create a video about AI?" → {{"intent": "mixed", "details": {{"has_greeting": true, "topic": "AI"}}, "confidence": "high"}}

User message: "{last_user_msg}"

Respond with JSON only:"""

        try:
            response = model.invoke([HumanMessage(content=intent_prompt)])
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            intent_data = json.loads(content)
            intent = intent_data.get("intent", "unknown")
            details = intent_data.get("details", {})
            
            logger.info(f"Intent classified: {intent} (confidence: {intent_data.get('confidence', 'unknown')})")
            
            return {
                **state,
                "intent": intent,
                "intent_details": details
            }
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {**state, "intent": "unknown"}
    
    return classify_intent


def create_supervisor_workflow(provider: Provider = "google"):
    """
    Create the supervisor workflow with intent classification and sub-agents
    
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
    Lazy initialization of supervisor workflow with intent classification
    """
    global supervisor_workflow
    
    if supervisor_workflow is None:
        try:
            # Use proper multi-agent supervisor with intent classification
            supervisor_workflow = create_supervisor_workflow()
            print("✅ Supervisor workflow initialized with intent classification and sub-agents")
        except Exception as e:
            print(f"⚠️  Error initializing multi-agent supervisor, falling back to simple: {e}")
            logger.error(f"Supervisor initialization error: {e}", exc_info=True)
            supervisor_workflow = create_simple_supervisor()
    
    return supervisor_workflow
