"""
Agent Execution Routes
Stream agent responses in real-time using Server-Sent Events
"""

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field

from agents import get_supervisor_workflow


router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ExecuteRequest(BaseModel):
    """
    Request model for agent execution
    """
    message: str = Field(..., description="User message to send to agents")
    thread_id: str | None = Field(None, description="Thread ID for conversation continuity")
    user_context: dict = Field(default_factory=dict, description="Additional user context")


class StreamEvent(BaseModel):
    """
    Stream event model for SSE
    """
    event: str  # message, tool_call, agent_switch, error, done
    data: dict[str, Any]
    timestamp: str


# ============================================================================
# Stream Event Generator
# ============================================================================

async def generate_stream_events(
    message: str,
    thread_id: str,
    user_context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events from agent execution
    
    Args:
        message: User message
        thread_id: Conversation thread ID
        user_context: Additional context
        
    Yields:
        SSE formatted strings
    """
    try:
        # Get supervisor workflow
        workflow = get_supervisor_workflow()
        
        # Prepare input state
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        
        input_state = {
            "messages": [HumanMessage(content=message)],
        }
        
        if user_context:
            input_state["user_context"] = user_context
        
        # Send start event
        yield format_sse_event({
            "event": "start",
            "data": {
                "thread_id": thread_id,
                "message": message,
            }
        })
        
        # Stream events from workflow
        current_agent = None
        
        async for event in workflow.astream_events(input_state, config, version="v2"):
            event_type = event.get("event")
            
            # Handle different event types
            if event_type == "on_chat_model_stream":
                # Stream LLM tokens
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    yield format_sse_event({
                        "event": "token",
                        "data": {
                            "token": chunk.content,
                            "agent": current_agent,
                        }
                    })
            
            elif event_type == "on_chat_model_end":
                # LLM call completed
                output = event.get("data", {}).get("output")
                if output:
                    # Check for tool calls
                    if hasattr(output, "tool_calls") and output.tool_calls:
                        for tool_call in output.tool_calls:
                            yield format_sse_event({
                                "event": "tool_call",
                                "data": {
                                    "tool_name": tool_call.get("name"),
                                    "tool_id": tool_call.get("id"),
                                    "args": tool_call.get("args"),
                                    "agent": current_agent,
                                }
                            })
                    
                    # Send complete message
                    if hasattr(output, "content") and output.content:
                        yield format_sse_event({
                            "event": "message",
                            "data": {
                                "content": output.content,
                                "agent": current_agent,
                                "type": "ai",
                            }
                        })
            
            elif event_type == "on_tool_start":
                # Tool execution started
                tool_name = event.get("name", "")
                tool_input = event.get("data", {}).get("input", {})
                
                yield format_sse_event({
                    "event": "tool_start",
                    "data": {
                        "tool_name": tool_name,
                        "input": tool_input,
                    }
                })
            
            elif event_type == "on_tool_end":
                # Tool execution completed
                tool_name = event.get("name", "")
                tool_output = event.get("data", {}).get("output")
                
                yield format_sse_event({
                    "event": "tool_end",
                    "data": {
                        "tool_name": tool_name,
                        "output": str(tool_output)[:500],  # Truncate long outputs
                    }
                })
            
            # Detect agent switches
            metadata = event.get("metadata", {})
            if "langgraph_node" in metadata:
                node_name = metadata["langgraph_node"]
                if node_name != current_agent:
                    current_agent = node_name
                    yield format_sse_event({
                        "event": "agent_switch",
                        "data": {
                            "agent": current_agent,
                        }
                    })
        
        # Send completion event
        yield format_sse_event({
            "event": "done",
            "data": {
                "thread_id": thread_id,
            }
        })
    
    except Exception as e:
        # Send error event
        yield format_sse_event({
            "event": "error",
            "data": {
                "error": str(e),
                "type": type(e).__name__,
            }
        })
        raise


def format_sse_event(data: dict) -> str:
    """
    Format data as Server-Sent Event
    
    Args:
        data: Event data dictionary
        
    Returns:
        SSE formatted string
    """
    event_type = data.get("event", "message")
    event_data = data.get("data", {})
    
    # Add timestamp if not present
    if "timestamp" not in event_data:
        from datetime import datetime
        event_data["timestamp"] = datetime.utcnow().isoformat()
    
    # Format as SSE
    sse_data = f"event: {event_type}\n"
    sse_data += f"data: {json.dumps(event_data)}\n\n"
    
    return sse_data


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/stream")
async def execute_stream(request: ExecuteRequest):
    """
    Execute agent workflow with streaming response
    
    Streams events in real-time using Server-Sent Events (SSE)
    
    Event types:
    - start: Execution started
    - token: Individual LLM token (streaming)
    - message: Complete message from agent
    - tool_call: Agent called a tool
    - tool_start: Tool execution started
    - tool_end: Tool execution completed
    - agent_switch: Supervisor switched to different agent
    - error: Error occurred
    - done: Execution completed
    """
    # Generate or use provided thread ID
    thread_id = request.thread_id or str(uuid.uuid4())
    
    # Create event generator
    event_generator = generate_stream_events(
        message=request.message,
        thread_id=thread_id,
        user_context=request.user_context,
    )
    
    # Return streaming response
    return StreamingResponse(
        event_generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/invoke")
async def execute_invoke(request: ExecuteRequest) -> dict:
    """
    Execute agent workflow and return complete result
    
    Non-streaming endpoint for simple integrations
    """
    try:
        # Get supervisor workflow
        workflow = get_supervisor_workflow()
        
        # Generate or use provided thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Prepare input state
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        
        input_state = {
            "messages": [HumanMessage(content=request.message)],
        }
        
        if request.user_context:
            input_state["user_context"] = request.user_context
        
        # Execute workflow
        result = await asyncio.to_thread(workflow.invoke, input_state, config)
        
        # Extract messages
        messages = []
        for msg in result.get("messages", []):
            if isinstance(msg, (HumanMessage, AIMessage)):
                messages.append({
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                })
            elif isinstance(msg, ToolMessage):
                messages.append({
                    "type": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id,
                })
        
        return {
            "thread_id": thread_id,
            "messages": messages,
            "status": "completed",
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
            }
        )


@router.get("/threads/{thread_id}")
async def get_thread_history(thread_id: str) -> dict:
    """
    Get conversation history for a thread
    
    Args:
        thread_id: Thread ID to retrieve
        
    Returns:
        Thread history with messages
    """
    try:
        workflow = get_supervisor_workflow()
        
        # Get state for thread
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }
        
        state = await asyncio.to_thread(workflow.get_state, config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Extract messages
        messages = []
        for msg in state.values.get("messages", []):
            if isinstance(msg, (HumanMessage, AIMessage)):
                messages.append({
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content,
                })
        
        return {
            "thread_id": thread_id,
            "messages": messages,
            "created_at": state.created_at.isoformat() if state.created_at else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
            }
        )
