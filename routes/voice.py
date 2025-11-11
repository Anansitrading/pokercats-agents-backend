"""
Voice Agent Routes
Real-time voice interaction using Gemini Live API with LangGraph tool calling
"""

import os
import asyncio
import json
import base64
from typing import AsyncGenerator, Callable
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Google Gemini imports
try:
    from google import genai
    from google.genai.types import (
        LiveConnectConfig,
        FunctionDeclaration,
        Tool,
        GenerateContentConfig,
    )
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️  Google Gemini SDK not installed. Install: pip install google-generativeai")
    GEMINI_AVAILABLE = False


router = APIRouter()


# ============================================================================
# Function Declarations for Voice Agent Tools
# ============================================================================

# Tool declarations that will call LangGraph sub-agents (only if Gemini available)
if GEMINI_AVAILABLE:
    generate_script_tool = FunctionDeclaration(
        name="generate_video_script",
        description="Generate a complete video script with ALT beats from user requirements. Use this when the user wants to create a video script or storyline.",
        parameters={
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "string",
                    "description": "User's video requirements including type, duration, audience, message, and tone"
                },
                "mode": {
                    "type": "string",
                    "enum": ["hitl", "yolo"],
                    "description": "Production mode: 'hitl' (ask for approvals) or 'yolo' (full auto)"
                }
            },
            "required": ["requirements"]
        }
    )

    plan_shots_tool = FunctionDeclaration(
        name="plan_video_shots",
        description="Plan detailed shot list from a video script. Use this when the user has a script and needs shot planning or storyboarding.",
        parameters={
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "Video script with ALT beats (JSON format)"
                }
            },
            "required": ["script"]
        }
    )

    create_production_plan_tool = FunctionDeclaration(
        name="create_production_plan",
        description="Create a production plan with AI tool recommendations and cost estimates. Use this when the user needs production planning or cost estimation.",
        parameters={
            "type": "object",
            "properties": {
                "shot_list": {
                    "type": "string",
                    "description": "Shot list with specifications (JSON format)"
                },
                "quality": {
                    "type": "string",
                    "enum": ["high", "balanced", "budget"],
                    "description": "Quality priority for tool selection"
                }
            },
            "required": ["shot_list"]
        }
    )

    full_pipeline_tool = FunctionDeclaration(
        name="run_full_video_pipeline",
        description="Run the complete video production pipeline from requirements to production plan. Use this when the user wants end-to-end video planning.",
        parameters={
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "string",
                    "description": "User's complete video requirements"
                },
                "quality": {
                    "type": "string",
                    "enum": ["high", "balanced", "budget"],
                    "description": "Quality priority"
                },
                "mode": {
                    "type": "string",
                    "enum": ["hitl", "yolo"],
                    "description": "Production mode"
                }
            },
            "required": ["requirements"]
        }
    )
else:
    # Fallback: set to None when Gemini not available
    generate_script_tool = None
    plan_shots_tool = None
    create_production_plan_tool = None
    full_pipeline_tool = None


# ============================================================================
# Tool Execution (calls LangGraph agents)
# ============================================================================

async def execute_tool_call(tool_name: str, parameters: dict) -> dict:
    """
    Execute tool by calling appropriate LangGraph agent
    
    Args:
        tool_name: Name of tool to execute
        parameters: Tool parameters
        
    Returns:
        Tool execution result
    """
    from ..agents import get_supervisor_workflow
    
    try:
        # Map tool calls to agent actions
        if tool_name == "generate_video_script":
            workflow = get_supervisor_workflow()
            result = await asyncio.to_thread(
                workflow.invoke,
                {
                    "messages": [{
                        "role": "user",
                        "content": f"Generate a video script for: {parameters.get('requirements')}"
                    }]
                },
                {"configurable": {"thread_id": "voice_session"}}
            )
            
            # Extract script from messages
            script_text = result.get("messages", [])[-1].content if result.get("messages") else "Error generating script"
            
            return {
                "success": True,
                "result": script_text,
                "tool": tool_name
            }
        
        elif tool_name == "plan_video_shots":
            workflow = get_supervisor_workflow()
            result = await asyncio.to_thread(
                workflow.invoke,
                {
                    "messages": [{
                        "role": "user",
                        "content": f"Plan shots for this script: {parameters.get('script')}"
                    }]
                },
                {"configurable": {"thread_id": "voice_session"}}
            )
            
            shots = result.get("messages", [])[-1].content if result.get("messages") else "Error planning shots"
            
            return {
                "success": True,
                "result": shots,
                "tool": tool_name
            }
        
        elif tool_name == "create_production_plan":
            workflow = get_supervisor_workflow()
            result = await asyncio.to_thread(
                workflow.invoke,
                {
                    "messages": [{
                        "role": "user",
                        "content": f"Create production plan for shots: {parameters.get('shot_list')} with quality: {parameters.get('quality', 'balanced')}"
                    }]
                },
                {"configurable": {"thread_id": "voice_session"}}
            )
            
            plan = result.get("messages", [])[-1].content if result.get("messages") else "Error creating plan"
            
            return {
                "success": True,
                "result": plan,
                "tool": tool_name
            }
        
        elif tool_name == "run_full_video_pipeline":
            # Run complete pipeline through orchestrator
            from workflows import ProductionOrchestrator
            
            orchestrator = ProductionOrchestrator(mode=parameters.get('mode', 'yolo'))
            
            # Build VRD from requirements
            vrd = {
                "project_name": "Voice Generated Video",
                "video_type": "general",
                "estimated_duration": "60s",
                "requirements": parameters.get('requirements')
            }
            
            # Execute pipeline
            result = await asyncio.to_thread(
                orchestrator.execute_full_pipeline,
                vrd,
                {"quality_priority": parameters.get('quality', 'balanced')}
            )
            
            # Format response
            summary = result.get('summary', {})
            response = f"""Complete pipeline executed successfully:
- Script: {summary.get('beats', 0)} ALT beats
- Shots: {summary.get('shots', 0)} shots planned
- Cost: ${summary.get('cost_usd', 0):.2f}
- Time: {summary.get('time_minutes', 0):.1f} minutes

Production plan ready!"""
            
            return {
                "success": True,
                "result": response,
                "tool": tool_name,
                "data": result
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name
        }


# ============================================================================
# Voice WebSocket Endpoint
# ============================================================================

@router.websocket("/live")
async def voice_agent_live(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interaction with LangGraph agents
    
    Uses Gemini Live API for:
    - Real-time voice input/output
    - Tool calling to LangGraph sub-agents
    - Streaming transcriptions
    - Audio streaming
    
    Client sends:
    - Audio chunks (PCM 16kHz, mono)
    - Control messages (start, stop, etc.)
    
    Server sends:
    - Audio responses (PCM 24kHz)
    - Transcriptions (input and output)
    - Tool call notifications
    - Agent state updates
    """
    if not GEMINI_AVAILABLE:
        await websocket.close(code=1011, reason="Gemini SDK not available")
        return
    
    await websocket.accept()
    
    try:
        # Initialize Gemini client
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Voice agent system instruction
        system_instruction = """You are an AI Video Production Assistant with access to a complete video production pipeline.

You can help users:
1. Generate video scripts with ALT beats (detailed narrative structure)
2. Plan shots and create storyboards
3. Select optimal AI tools for production
4. Estimate costs and timelines
5. Run the complete pipeline from idea to production plan

**Available Tools:**
- generate_video_script: Create structured scripts with 8-part narrative
- plan_video_shots: Convert scripts to detailed shot lists
- create_production_plan: Select AI tools and estimate costs
- run_full_video_pipeline: Execute complete workflow automatically

**Guidelines:**
- Listen carefully to user needs
- Ask clarifying questions when needed
- Use tools proactively
- Explain technical decisions clearly
- Provide concrete, actionable plans

Be conversational, helpful, and efficient."""
        
        # Configure live session
        config = LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config={
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Aoede"  # Professional voice
                    }
                }
            }
        )
        
        # Start live session
        async with client.aio.live.connect(
            model="gemini-2.5-flash-preview-0205",  # Latest with Live API
            config=config
        ) as session:
            
            # Send system instruction
            await session.send(
                {"text": system_instruction},
                end_of_turn=True
            )
            
            # Handle bidirectional streaming
            async def receive_from_client():
                """Receive audio from client and send to Gemini"""
                try:
                    while True:
                        message = await websocket.receive()
                        
                        if "bytes" in message:
                            # Audio chunk from client
                            audio_data = message["bytes"]
                            
                            # Encode for Gemini (base64)
                            audio_base64 = base64.b64encode(audio_data).decode()
                            
                            # Send to Gemini
                            await session.send({
                                "data": audio_base64,
                                "mime_type": "audio/pcm"
                            })
                        
                        elif "text" in message:
                            # Text message (control or fallback)
                            text = message["text"]
                            
                            if text == "END_TURN":
                                # Client finished speaking
                                await session.send({}, end_of_turn=True)
                            else:
                                # Text input
                                await session.send({"text": text}, end_of_turn=True)
                
                except WebSocketDisconnect:
                    print("Client disconnected")
                except Exception as e:
                    print(f"Error receiving from client: {e}")
            
            async def send_to_client():
                """Receive from Gemini and send to client"""
                try:
                    async for response in session.receive():
                        
                        # Handle tool calls
                        if hasattr(response, "tool_call") and response.tool_call:
                            tool_call = response.tool_call
                            
                            # Notify client about tool call
                            await websocket.send_json({
                                "type": "tool_call",
                                "tool": tool_call.function_calls[0].name if tool_call.function_calls else "unknown",
                                "status": "executing"
                            })
                            
                            # Execute tool via LangGraph
                            tool_result = await execute_tool_call(
                                tool_call.function_calls[0].name,
                                tool_call.function_calls[0].args
                            )
                            
                            # Send result back to Gemini
                            await session.send({
                                "tool_response": {
                                    "function_responses": [{
                                        "id": tool_call.function_calls[0].id,
                                        "name": tool_call.function_calls[0].name,
                                        "response": tool_result
                                    }]
                                }
                            })
                            
                            # Notify client tool completed
                            await websocket.send_json({
                                "type": "tool_complete",
                                "tool": tool_call.function_calls[0].name,
                                "success": tool_result.get("success", False)
                            })
                        
                        # Handle audio responses
                        if hasattr(response, "data") and response.data:
                            # Decode audio
                            audio_bytes = base64.b64decode(response.data)
                            
                            # Send to client
                            await websocket.send_bytes(audio_bytes)
                        
                        # Handle transcriptions
                        if hasattr(response, "text") and response.text:
                            await websocket.send_json({
                                "type": "transcription",
                                "role": "assistant",
                                "text": response.text
                            })
                
                except Exception as e:
                    print(f"Error sending to client: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "error": str(e)
                    })
            
            # Run bidirectional streaming
            await asyncio.gather(
                receive_from_client(),
                send_to_client()
            )
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Voice agent error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# Text Message WebSocket Endpoint (for Next.js integration)
# ============================================================================

@router.websocket("/stream")
async def voice_stream_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice/text input → agent execution → streaming results
    
    Client sends:
    {
      "type": "voice_input" | "message",
      "data": "...",  // audio or text
      "context": {}   // optional context
    }
    
    Server sends:
    {
      "type": "agent_started" | "agent_message" | "tool_call_start" | etc.,
      "agent": "vrd_agent",
      "data": {...}
    }
    """
    # Accept connection
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Route based on message type
            if message["type"] == "voice_input":
                await handle_voice_input(websocket, message)
            elif message["type"] == "message":
                await handle_text_message(websocket, message)
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": f"Unknown message type: {message['type']}"
                }))
    
    except WebSocketDisconnect:
        print("Client disconnected from /stream endpoint")
    except Exception as e:
        print(f"WebSocket error in /stream: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": str(e)
            }))
        except:
            pass


async def handle_text_message(websocket: WebSocket, message: dict):
    """Handle text message from client"""
    from ..agents import get_supervisor_workflow
    
    text = message.get("message", "")
    context = message.get("context", {})
    
    # Get supervisor workflow
    workflow = get_supervisor_workflow()
    
    # Send agent started event
    await websocket.send_text(json.dumps({
        "type": "agent_started",
        "agent": "supervisor",
        "task": text
    }))
    
    # Execute workflow with streaming
    config = {"configurable": {"thread_id": "web_session"}}
    
    try:
        # Stream events from LangGraph
        async for event in workflow.astream_events(
            {"messages": [{"role": "user", "content": text}]},
            config,
            version="v2"
        ):
            # Parse LangGraph events and send to client
            event_type = event.get("event")
            
            if event_type == "on_chat_model_stream":
                # Stream agent messages
                chunk = event["data"].get("chunk", {})
                content = chunk.get("content", "") if isinstance(chunk, dict) else str(chunk)
                
                await websocket.send_text(json.dumps({
                    "type": "agent_message",
                    "agent": event.get("name", "unknown"),
                    "message": content
                }))
            
            elif event_type == "on_tool_start":
                # Tool call started
                await websocket.send_text(json.dumps({
                    "type": "tool_call_start",
                    "agent": event.get("name", "unknown"),
                    "tool": event["data"].get("name", "unknown"),
                    "args": event["data"].get("input", {})
                }))
            
            elif event_type == "on_tool_end":
                # Tool call completed
                result = event["data"].get("output", {})
                
                await websocket.send_text(json.dumps({
                    "type": "tool_call_end",
                    "agent": event.get("name", "unknown"),
                    "tool": event["data"].get("name", "unknown"),
                    "result": result
                }))
                
                # Check if asset was generated
                if isinstance(result, dict) and "url" in result:
                    await websocket.send_text(json.dumps({
                        "type": "asset_generated",
                        "url": result["url"],
                        "asset_type": result.get("type", "image"),
                        "metadata": result.get("metadata", {})
                    }))
        
        # Send completion event
        await websocket.send_text(json.dumps({
            "type": "completed",
            "result": "Task completed successfully"
        }))
    
    except Exception as e:
        print(f"Error in handle_text_message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))


async def handle_voice_input(websocket: WebSocket, message: dict):
    """Handle voice input from client"""
    # TODO: Implement voice-to-text conversion
    # For now, treat as text
    text_message = {
        "type": "message",
        "message": message.get("data", ""),
        "context": message.get("context", {})
    }
    await handle_text_message(websocket, text_message)


# ============================================================================
# Voice Agent Status Endpoint
# ============================================================================

class VoiceStatusResponse(BaseModel):
    """Voice agent status"""
    available: bool
    model: str
    features: list[str]
    error: str | None = None


@router.get("/status")
async def voice_agent_status() -> VoiceStatusResponse:
    """
    Get voice agent availability and features
    """
    if not GEMINI_AVAILABLE:
        return VoiceStatusResponse(
            available=False,
            model="none",
            features=[],
            error="Google Gemini SDK not installed"
        )
    
    if not os.getenv("GOOGLE_API_KEY"):
        return VoiceStatusResponse(
            available=False,
            model="none",
            features=[],
            error="GOOGLE_API_KEY not configured"
        )
    
    return VoiceStatusResponse(
        available=True,
        model="gemini-2.5-flash-preview-0205",
        features=[
            "real_time_voice",
            "tool_calling",
            "langgraph_integration",
            "streaming_audio",
            "transcription",
        ]
    )
