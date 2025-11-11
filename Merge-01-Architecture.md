# Merge-01: Integration Architecture

**Prerequisites:** Merge-00 complete, main code merged into feature branch  
**Objective:** Design integration layer between FastAPI agents and Next.js video editor

---

## 🎯 Integration Strategy: Hybrid API Bridge

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (Next.js App)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  RightPanel.tsx (Chat UI)                                  │ │
│  │    ↓                                                        │ │
│  │  AgentBridgeService.ts (NEW)                              │ │
│  │    ├─→ WebSocket connection to FastAPI                    │ │
│  │    └─→ Stream events to UI                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓ HTTP/WebSocket                      │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│              FastAPI Server (Python) - Port 8000                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  /agents/voice/stream (NEW)                               │ │
│  │    ↓                                                        │ │
│  │  Voice → LangGraph Supervisor                             │ │
│  │           ↓                                                 │ │
│  │  Sub-agents (VRD, ScriptSmith, ShotMaster, VideoSolver)  │ │
│  │           ↓                                                 │ │
│  │  Tools (ALT beats, shot planning, tool selection)         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           ↓ Results                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                    Back to Browser                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  gemini-agent-store.ts (Zustand)                          │ │
│  │    ↓                                                        │ │
│  │  Timeline (Add clips from agent results)                  │ │
│  │  Media Panel (Show generated assets)                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Components to Build

### 1. FastAPI Voice Endpoint (New)
**File:** `apps/agents/routes/voice.py`

**Purpose:** WebSocket endpoint for voice input → agent execution → streaming results

**Features:**
- Accept voice audio or text from browser
- Route to LangGraph supervisor
- Stream agent events back to browser
- Track session state

### 2. Agent Bridge Service (New)
**File:** `apps/web/src/services/agent-bridge-service.ts`

**Purpose:** TypeScript client for FastAPI agents

**Features:**
- WebSocket connection management
- Event parsing and transformation
- Error handling and reconnection
- Type-safe interface matching FastAPI

### 3. Enhanced RightPanel (Modified)
**File:** `apps/web/src/components/kijko-agent/RightPanel.tsx`

**Purpose:** Update chat UI to use LangGraph agents

**Changes:**
- Add toggle: "Direct Gemini" vs "LangGraph Agents"
- Route voice/text through AgentBridgeService
- Display agent reasoning and tool calls
- Show sub-agent attribution

### 4. Zustand Store Updates (Modified)
**File:** `apps/web/src/stores/gemini-agent-store.ts`

**Purpose:** Track agent state alongside Gemini state

**Additions:**
- `agentMode: 'gemini' | 'langgraph'`
- `activeAgents: string[]` (VRD, ScriptSmith, etc.)
- `agentEvents: AgentEvent[]`
- `toolCalls: ToolCall[]`

---

## 🔄 Data Flow

### Voice Input Flow

```typescript
// 1. User speaks or types in RightPanel
User → RightPanel.tsx
         ↓
// 2. Send to agent bridge
AgentBridgeService.sendVoiceInput(audio)
         ↓
// 3. WebSocket to FastAPI
WebSocket → ws://localhost:8000/agents/voice/stream
         ↓
// 4. FastAPI routes to LangGraph
VoiceHandler → Supervisor → VRD Agent
         ↓
// 5. Agent generates VRD
VRD Tool → Returns structured requirements
         ↓
// 6. Stream back to browser
WebSocket Event → AgentBridgeService
         ↓
// 7. Update UI
RightPanel displays VRD + asks user to confirm
```

### Asset Generation Flow

```typescript
// 1. Agent decides to generate asset
ScriptSmith → "Need image for Hook scene"
         ↓
// 2. Calls tool
Tool: generate_image(prompt="Product on desk, professional lighting")
         ↓
// 3. Tool calls external API (fal.ai, Freepik, etc.)
ExternalAPI → Returns image URL
         ↓
// 4. Stream result to browser
WebSocket Event: { type: 'asset_generated', url: '...', agent: 'ScriptSmith' }
         ↓
// 5. Zustand store adds asset
gemini-agent-store.addGeminiAsset({ url, type: 'image', agent: 'ScriptSmith' })
         ↓
// 6. UI updates
Media Panel shows new image + Timeline can use it
```

---

## 🧩 Integration Points

### Point 1: Voice Input
**Current:** `RightPanel.tsx` → `geminiService.startLiveConversationWithRecovery()`  
**New:** `RightPanel.tsx` → `AgentBridgeService.startAgentVoiceSession()`

### Point 2: Asset Display
**Current:** `gemini-agent-store.addGeminiAsset()` for Gemini results  
**New:** Same store, same function, just different source

### Point 3: Timeline Integration
**Current:** Drag assets from Media Panel to Timeline  
**New:** Same workflow, assets now come from agents too

### Point 4: Chat History
**Current:** `chatHistory` in Zustand store  
**New:** Add `agentAttribution` field to show which agent responded

---

## 📦 New Dependencies

### Web App (TypeScript)
```json
// apps/web/package.json additions
{
  "dependencies": {
    "socket.io-client": "^4.7.0",  // WebSocket client
    "eventemitter3": "^5.0.1"       // Event handling
  }
}
```

### Agents App (Python)
```txt
# apps/agents/requirements.txt additions
websockets>=12.0
python-socketio>=5.11.0
```

---

## 🎨 UI/UX Changes

### RightPanel Header
```tsx
// Add mode toggle
<div className="flex items-center gap-2">
  <label className="text-xs">Agent Mode:</label>
  <select value={agentMode} onChange={handleModeChange}>
    <option value="gemini">Direct Gemini</option>
    <option value="langgraph">LangGraph Agents</option>
  </select>
</div>
```

### Chat Messages with Agent Attribution
```tsx
// Before
<div className="message">
  <p>{message.content}</p>
</div>

// After
<div className="message">
  {message.agent && (
    <div className="text-xs text-gray-400">
      <Icon name="agent" /> {message.agent}
    </div>
  )}
  <p>{message.content}</p>
</div>
```

### Tool Call Indicators
```tsx
// New component
<div className="tool-call">
  <Icon name="tool" />
  <span>ScriptSmith using generate_alt_beats...</span>
  <Spinner />
</div>
```

---

## 🔧 Configuration

### Environment Variables

**Web App** (`.env.local`)
```bash
# Add agents API endpoint
NEXT_PUBLIC_AGENTS_API_URL=http://localhost:8000
NEXT_PUBLIC_AGENTS_WS_URL=ws://localhost:8000
```

**Agents App** (`.env`)
```bash
# Add CORS for web app
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 📊 Success Criteria

Integration complete when:

- [ ] User can toggle between Gemini and LangGraph modes
- [ ] Voice input routes to LangGraph supervisor
- [ ] Agent responses stream to chat UI
- [ ] Tool calls visible in UI with agent attribution
- [ ] Generated assets appear in Media Panel
- [ ] Assets draggable to Timeline
- [ ] Error handling graceful
- [ ] Observability logs all agent activity

---

## 🔍 Context Needed for Implementation

### Perplexity Searches

**Query 1: WebSocket Integration**
```
Next.js WebSocket client integration with FastAPI 2025:
- socket.io-client vs native WebSocket
- Connection lifecycle management
- Auto-reconnection strategies
- Typed event handling in TypeScript
- Error handling best practices
```

**Query 2: Real-time UI Updates**
```
React real-time UI updates from WebSocket events:
- Zustand store updates from WebSocket
- Optimistic updates vs server state
- Message deduplication strategies
- Streaming text rendering
- Loading states for async tool calls
```

**Query 3: Microservice Architecture**
```
Next.js + FastAPI microservice integration patterns:
- CORS configuration for local development
- API gateway patterns
- WebSocket proxying in production
- Error propagation between services
- Health checks and monitoring
```

### Context7 Documentation

```typescript
// Get Next.js documentation
await mcp0_resolve_library_id({ libraryName: "next.js" })
await mcp0_get_library_docs({
  context7CompatibleLibraryID: "/vercel/next.js",
  topic: "api routes websocket proxy server actions",
  tokens: 3000
})

// Get socket.io documentation
await mcp0_resolve_library_id({ libraryName: "socket.io" })
await mcp0_get_library_docs({
  context7CompatibleLibraryID: "/socketio/socket.io",
  topic: "client connection events error handling typescript",
  tokens: 2000
})
```

### Exa Code Context

```typescript
await mcp1_get_code_context_exa({
  query: "Next.js WebSocket client integration with FastAPI backend real-time updates",
  tokensNum: 5000
})

await mcp1_get_code_context_exa({
  query: "Zustand store updates from WebSocket events TypeScript",
  tokensNum: 3000
})
```

### Raindrop Documentation

Search Raindrop for:
- "fastapi websocket"
- "socket.io next.js"
- "react real-time updates"
- "microservice architecture patterns"

---

**Next:** Proceed to `Merge-02-API-Bridge.md` for detailed implementation
