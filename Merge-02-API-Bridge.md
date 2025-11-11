# Merge-02: API Bridge Implementation

**Prerequisites:** Merge-00 & Merge-01 complete  
**Objective:** Build TypeScript service to communicate with FastAPI agents

---

## 🎯 Overview

Create `AgentBridgeService` to handle all communication between Next.js app and FastAPI agents system.

**File:** `apps/web/src/services/agent-bridge-service.ts`

---

## 📋 Implementation

### Service Architecture

```typescript
/**
 * Agent Bridge Service
 * Connects Next.js video editor to LangGraph agents via WebSocket
 */

import { EventEmitter } from 'eventemitter3';

// Event types from FastAPI agents
export type AgentEvent = 
  | { type: 'agent_started', agent: string, task: string }
  | { type: 'agent_message', agent: string, message: string }
  | { type: 'tool_call_start', agent: string, tool: string, args: any }
  | { type: 'tool_call_end', agent: string, tool: string, result: any }
  | { type: 'asset_generated', url: string, type: 'image' | 'video', metadata: any }
  | { type: 'error', agent: string, error: string }
  | { type: 'completed', result: any };

// Service configuration
export interface AgentBridgeConfig {
  apiUrl: string;       // http://localhost:8000
  wsUrl: string;        // ws://localhost:8000
  autoReconnect: boolean;
  reconnectDelay: number;
}

export class AgentBridgeService extends EventEmitter {
  private ws: WebSocket | null = null;
  private config: AgentBridgeConfig;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  constructor(config: AgentBridgeConfig) {
    super();
    this.config = config;
  }

  /**
   * Connect to FastAPI agents WebSocket
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.config.wsUrl}/agents/voice/stream`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[AgentBridge] Connected to agents');
        this.reconnectAttempts = 0;
        this.emit('connected');
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const data: AgentEvent = JSON.parse(event.data);
          this.handleAgentEvent(data);
        } catch (error) {
          console.error('[AgentBridge] Parse error:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[AgentBridge] WebSocket error:', error);
        this.emit('error', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('[AgentBridge] Disconnected');
        this.emit('disconnected');
        
        if (this.config.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => this.connect(), this.config.reconnectDelay);
        }
      };
    });
  }

  /**
   * Send voice input to agents
   */
  sendVoiceInput(input: { type: 'audio' | 'text', data: string | ArrayBuffer }): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.ws.send(JSON.stringify({
      type: 'voice_input',
      ...input
    }));
  }

  /**
   * Send text message to agents
   */
  sendMessage(message: string, context?: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.ws.send(JSON.stringify({
      type: 'message',
      message,
      context
    }));
  }

  /**
   * Handle incoming agent events
   */
  private handleAgentEvent(event: AgentEvent): void {
    // Emit typed event
    this.emit('agent_event', event);

    // Emit specific event types
    this.emit(event.type, event);
  }

  /**
   * Disconnect from agents
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Get connection status
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
let agentBridge: AgentBridgeService | null = null;

export function getAgentBridge(): AgentBridgeService {
  if (!agentBridge) {
    agentBridge = new AgentBridgeService({
      apiUrl: process.env.NEXT_PUBLIC_AGENTS_API_URL || 'http://localhost:8000',
      wsUrl: process.env.NEXT_PUBLIC_AGENTS_WS_URL || 'ws://localhost:8000',
      autoReconnect: true,
      reconnectDelay: 2000,
    });
  }
  return agentBridge;
}
```

---

## 🔧 FastAPI WebSocket Endpoint

**File:** `apps/agents/routes/voice.py` (NEW)

```python
"""
Voice WebSocket endpoint for browser integration
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import AsyncGenerator
import json
import asyncio

from agents.supervisor import get_supervisor_workflow
from agents.observability import get_observability, logger

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_event(self, websocket: WebSocket, event: dict):
        """Send typed event to client"""
        await websocket.send_text(json.dumps(event))


manager = ConnectionManager()


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
    await manager.connect(websocket)
    
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
                await manager.send_event(websocket, {
                    "type": "error",
                    "error": f"Unknown message type: {message['type']}"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.send_event(websocket, {
            "type": "error",
            "error": str(e)
        })
        manager.disconnect(websocket)


async def handle_text_message(websocket: WebSocket, message: dict):
    """Handle text message from client"""
    
    text = message.get("message", "")
    context = message.get("context", {})
    
    # Get supervisor workflow
    workflow = get_supervisor_workflow()
    
    # Send agent started event
    await manager.send_event(websocket, {
        "type": "agent_started",
        "agent": "supervisor",
        "task": text
    })
    
    # Execute workflow with streaming
    config = {"configurable": {"thread_id": "web_session"}}
    
    async for event in workflow.astream_events(
        {"messages": [{"role": "user", "content": text}]},
        config,
        version="v2"
    ):
        # Parse LangGraph events and send to client
        event_type = event.get("event")
        
        if event_type == "on_chat_model_stream":
            # Stream agent messages
            chunk = event["data"]["chunk"]
            await manager.send_event(websocket, {
                "type": "agent_message",
                "agent": event.get("name", "unknown"),
                "message": chunk.content if hasattr(chunk, 'content') else str(chunk)
            })
        
        elif event_type == "on_tool_start":
            # Tool call started
            await manager.send_event(websocket, {
                "type": "tool_call_start",
                "agent": event.get("name", "unknown"),
                "tool": event["data"].get("name", "unknown"),
                "args": event["data"].get("input", {})
            })
        
        elif event_type == "on_tool_end":
            # Tool call completed
            result = event["data"].get("output", {})
            
            await manager.send_event(websocket, {
                "type": "tool_call_end",
                "agent": event.get("name", "unknown"),
                "tool": event["data"].get("name", "unknown"),
                "result": result
            })
            
            # Check if asset was generated
            if isinstance(result, dict) and "url" in result:
                await manager.send_event(websocket, {
                    "type": "asset_generated",
                    "url": result["url"],
                    "asset_type": result.get("type", "image"),
                    "metadata": result.get("metadata", {})
                })
    
    # Send completion event
    await manager.send_event(websocket, {
        "type": "completed",
        "result": "Task completed successfully"
    })


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
```

**Update:** `apps/agents/main.py`

```python
# Add import
from .routes.voice import router as voice_router

# Include router
app.include_router(voice_router, prefix="/agents/voice", tags=["voice"])
```

---

## 🔍 Context for Implementation

### Perplexity Searches

**Query 1: FastAPI WebSocket Streaming**
```
FastAPI WebSocket streaming best practices 2025:
- Async event streaming patterns
- Connection lifecycle management
- Error handling in WebSocket routes
- Broadcasting to multiple clients
- LangGraph astream_events integration
```

**Query 2: TypeScript WebSocket Client**
```
TypeScript WebSocket client with EventEmitter:
- Type-safe event handling
- Reconnection strategies
- Message queuing during disconnect
- Error recovery patterns
- Browser WebSocket API best practices
```

**Query 3: Next.js Environment Variables**
```
Next.js 15 environment variables:
- NEXT_PUBLIC_ prefix for client-side
- Runtime vs build-time variables
- Type-safe env with Zod
- Development vs production config
```

### Context7 Documentation

```typescript
await mcp0_get_library_docs({
  context7CompatibleLibraryID: "/tiangolo/fastapi",
  topic: "websocket async streaming events error handling",
  tokens: 3000
})
```

### Exa Code Context

```typescript
await mcp1_get_code_context_exa({
  query: "FastAPI WebSocket streaming to React client TypeScript",
  tokensNum: 5000
})
```

---

## ✅ Testing

### Test WebSocket Connection

**Browser Console:**
```javascript
const ws = new WebSocket('ws://localhost:8000/agents/voice/stream');

ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));

// Send test message
ws.send(JSON.stringify({
  type: 'message',
  message: 'Create a 30-second product demo video'
}));
```

### Test AgentBridgeService

**React Component:**
```typescript
import { getAgentBridge } from '@/services/agent-bridge-service';

function TestComponent() {
  useEffect(() => {
    const bridge = getAgentBridge();
    
    bridge.on('connected', () => console.log('Bridge connected'));
    bridge.on('agent_message', (event) => console.log('Agent:', event));
    
    bridge.connect().then(() => {
      bridge.sendMessage('Test message');
    });
    
    return () => bridge.disconnect();
  }, []);
  
  return <div>Testing Agent Bridge...</div>;
}
```

---

## 📊 Success Criteria

- [ ] WebSocket connection established
- [ ] Text messages sent to agents
- [ ] Agent events received in browser
- [ ] Reconnection works after disconnect
- [ ] Error handling graceful
- [ ] TypeScript types match FastAPI events

---

**Next:** Proceed to `Merge-03-UI-Integration.md`
