# Merge-03: UI Integration

**Prerequisites:** Merge-02 complete (API bridge working)  
**Objective:** Update React components to use LangGraph agents

---

## 🎯 Overview

Modify existing chat UI to support both Gemini Live and LangGraph agents with seamless switching.

---

## 📋 Component Updates

### 1. Update RightPanel Component

**File:** `apps/web/src/components/kijko-agent/RightPanel.tsx`

**Changes:**

```typescript
import { useEffect, useState, useMemo } from 'react';
import { getAgentBridge, type AgentEvent } from '@/services/agent-bridge-service';
import type { ChatMessage, AgentMode, AspectRatio, AttachedFile, MediaAsset } from '../types';
import { useGeminiAgentStore } from '@/stores/gemini-agent-store';

// Add new state for agent mode
export const RightPanel: React.FC<RightPanelProps> = ({ /* ... */ }) => {
  // Existing state...
  const [agentSystem, setAgentSystem] = useState<'gemini' | 'langgraph'>('gemini');
  const [agentBridge] = useState(() => getAgentBridge());
  const [activeAgents, setActiveAgents] = useState<string[]>([]);
  
  // Connect to agent bridge on mount
  useEffect(() => {
    if (agentSystem === 'langgraph') {
      // Connect to FastAPI agents
      agentBridge.connect().catch(error => {
        console.error('Failed to connect to agents:', error);
        setChatHistory(prev => [...prev, {
          role: 'system',
          content: '⚠️ Failed to connect to LangGraph agents. Using Gemini fallback.'
        }]);
        setAgentSystem('gemini'); // Fallback to Gemini
      });
      
      // Listen to agent events
      agentBridge.on('agent_started', handleAgentStarted);
      agentBridge.on('agent_message', handleAgentMessage);
      agentBridge.on('tool_call_start', handleToolCallStart);
      agentBridge.on('tool_call_end', handleToolCallEnd);
      agentBridge.on('asset_generated', handleAssetGenerated);
      agentBridge.on('error', handleAgentError);
      agentBridge.on('completed', handleAgentCompleted);
      
      return () => {
        agentBridge.disconnect();
        agentBridge.removeAllListeners();
      };
    }
  }, [agentSystem]);
  
  // Agent event handlers
  const handleAgentStarted = (event: any) => {
    setActiveAgents(prev => [...prev, event.agent]);
    setChatHistory(prev => [...prev, {
      role: 'system',
      content: `🤖 ${event.agent} started: ${event.task}`,
      agent: event.agent
    }]);
  };
  
  const handleAgentMessage = (event: any) => {
    setChatHistory(prev => {
      const lastMsg = prev[prev.length - 1];
      
      // If last message is from same agent, append
      if (lastMsg?.agent === event.agent && lastMsg.role === 'assistant') {
        return [
          ...prev.slice(0, -1),
          { ...lastMsg, content: lastMsg.content + event.message }
        ];
      }
      
      // Otherwise, new message
      return [...prev, {
        role: 'assistant',
        content: event.message,
        agent: event.agent
      }];
    });
  };
  
  const handleToolCallStart = (event: any) => {
    setChatHistory(prev => [...prev, {
      role: 'system',
      content: `🔧 ${event.agent} calling ${event.tool}...`,
      agent: event.agent,
      toolCall: { name: event.tool, args: event.args, status: 'running' }
    }]);
  };
  
  const handleToolCallEnd = (event: any) => {
    setChatHistory(prev => {
      const lastToolCallIndex = prev.findLastIndex(
        msg => msg.toolCall?.name === event.tool && msg.toolCall?.status === 'running'
      );
      
      if (lastToolCallIndex >= 0) {
        const updated = [...prev];
        updated[lastToolCallIndex] = {
          ...updated[lastToolCallIndex],
          content: `✅ ${event.agent} completed ${event.tool}`,
          toolCall: { ...updated[lastToolCallIndex].toolCall!, status: 'success', result: event.result }
        };
        return updated;
      }
      
      return prev;
    });
  };
  
  const handleAssetGenerated = (event: any) => {
    // Add to Zustand store (same as Gemini)
    useGeminiAgentStore.getState().addGeminiAsset({
      url: event.url,
      type: event.asset_type,
      prompt: event.metadata?.prompt || '',
      timestamp: Date.now(),
      agent: event.metadata?.agent || 'unknown'
    });
    
    setChatHistory(prev => [...prev, {
      role: 'assistant',
      content: `🎨 Generated ${event.asset_type}`,
      mediaUrl: event.url,
      agent: event.metadata?.agent
    }]);
  };
  
  const handleAgentError = (event: any) => {
    setChatHistory(prev => [...prev, {
      role: 'system',
      content: `❌ Error from ${event.agent}: ${event.error}`
    }]);
    setActiveAgents(prev => prev.filter(a => a !== event.agent));
  };
  
  const handleAgentCompleted = (event: any) => {
    setActiveAgents([]);
    setChatHistory(prev => [...prev, {
      role: 'system',
      content: '✅ All agents completed'
    }]);
  };
  
  // Update submit handler
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    
    if (agentSystem === 'langgraph') {
      // Send to LangGraph agents
      setChatHistory(prev => [...prev, { role: 'user', content: prompt }]);
      agentBridge.sendMessage(prompt, {
        mode: detectedAgentMode,
        aspectRatio,
        attachedFiles,
        selectedAsset: selectedAssetForEdit
      });
      setPrompt('');
      setAttachedFiles([]);
    } else if (isLive) {
      // Existing Gemini Live logic
      geminiService.sendLiveText(prompt);
      // ...
    } else {
      // Existing Gemini logic
      onAgentSubmit(prompt, detectedAgentMode, { /* ... */ });
      // ...
    }
  };
  
  return (
    <div className="w-96 bg-gray-800 flex flex-col border-l border-gray-700">
      <div className="p-4 border-b border-gray-700 flex-shrink-0">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Generation Agent</h2>
          
          {/* Add agent system toggle */}
          <div className="flex items-center gap-2">
            <select 
              value={agentSystem} 
              onChange={e => setAgentSystem(e.target.value as 'gemini' | 'langgraph')}
              className="bg-gray-700 text-xs rounded px-2 py-1"
            >
              <option value="gemini">Gemini Direct</option>
              <option value="langgraph">LangGraph Agents</option>
            </select>
            <button className="p-1 rounded hover:bg-gray-700">
              <Icon name="history" />
            </button>
          </div>
        </div>
        
        {/* Show active agents indicator */}
        {agentSystem === 'langgraph' && activeAgents.length > 0 && (
          <div className="mt-2 flex gap-2 flex-wrap">
            {activeAgents.map(agent => (
              <span key={agent} className="text-xs bg-indigo-900 px-2 py-1 rounded">
                <Icon name="agent" className="inline w-3 h-3 mr-1" />
                {agent}
              </span>
            ))}
          </div>
        )}
        
        {/* Rest of existing UI... */}
      </div>
      
      {/* Chat messages with agent attribution */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {chatHistory.map((msg, index) => renderMessageWithAgent(msg, index))}
        {/* ... */}
      </div>
      
      {/* Input form - same as before */}
      <div className="p-4 border-t border-gray-700 flex-shrink-0">
        {/* ... */}
      </div>
    </div>
  );
};

// Update message rendering to show agent attribution
const renderMessageWithAgent = (msg: ChatMessage, index: number) => {
  if (msg.role === 'system') {
    return (
      <div key={index} className="text-center text-xs text-gray-500 my-2">
        {msg.content}
        {msg.toolCall && (
          <div className="mt-1 text-xs font-mono">
            {msg.toolCall.status === 'running' && <Spinner className="inline w-3 h-3" />}
            {msg.toolCall.status === 'success' && '✓'}
          </div>
        )}
      </div>
    );
  }
  
  const isUser = msg.role === 'user';
  
  return (
    <div key={index} className={`flex items-start gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`p-3 rounded-lg max-w-sm lg:max-w-md ${isUser ? 'bg-indigo-600' : 'bg-gray-700'}`}>
        {/* Agent attribution */}
        {!isUser && msg.agent && (
          <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
            <Icon name="agent" className="w-3 h-3" />
            <span>{msg.agent}</span>
          </div>
        )}
        
        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
        
        {msg.mediaUrl && (
          <img src={msg.mediaUrl} alt="generated media" className="mt-2 rounded-md max-h-48" />
        )}
      </div>
      
      {isUser && (
        <div className="p-2 bg-gray-700 rounded-full mt-1">
          <Icon name={msg.inputType === 'voice' ? 'mic' : 'keyboard'} className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
```

---

### 2. Update Zustand Store

**File:** `apps/web/src/stores/gemini-agent-store.ts`

**Changes:**

```typescript
interface GeminiAgentState {
  // Existing fields...
  
  // Add agent system tracking
  agentSystem: 'gemini' | 'langgraph';
  activeAgents: string[];
  agentEvents: AgentEvent[];
  
  // Actions
  setAgentSystem: (system: 'gemini' | 'langgraph') => void;
  addAgentEvent: (event: AgentEvent) => void;
  setActiveAgents: (agents: string[]) => void;
}

export const useGeminiAgentStore = create<GeminiAgentState>((set) => ({
  // Existing state...
  agentSystem: 'gemini',
  activeAgents: [],
  agentEvents: [],
  
  // New actions
  setAgentSystem: (system) => set({ agentSystem: system }),
  
  addAgentEvent: (event) =>
    set((state) => ({
      agentEvents: [...state.agentEvents, event]
    })),
  
  setActiveAgents: (agents) => set({ activeAgents: agents }),
  
  // Existing actions...
}));
```

---

### 3. Update Types

**File:** `apps/web/src/types/gemini-agent.ts` (or similar)

**Add:**

```typescript
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  inputType?: 'text' | 'voice';
  mediaUrl?: string;
  isLiveOutput?: boolean;
  
  // New fields for LangGraph
  agent?: string;           // Which agent sent this message
  toolCall?: {
    name: string;
    args: any;
    status: 'running' | 'success' | 'error';
    result?: any;
  };
}

export interface AgentEvent {
  type: 'agent_started' | 'agent_message' | 'tool_call_start' | 'tool_call_end' | 'asset_generated' | 'error' | 'completed';
  agent?: string;
  message?: string;
  tool?: string;
  args?: any;
  result?: any;
  url?: string;
  asset_type?: 'image' | 'video';
  metadata?: any;
  error?: string;
}
```

---

## 🎨 UI Enhancements

### Agent Status Indicator

Create new component: `apps/web/src/components/kijko-agent/AgentStatus.tsx`

```typescript
interface AgentStatusProps {
  activeAgents: string[];
  agentSystem: 'gemini' | 'langgraph';
}

export const AgentStatus: React.FC<AgentStatusProps> = ({ activeAgents, agentSystem }) => {
  if (agentSystem !== 'langgraph') return null;
  
  return (
    <div className="flex items-center gap-2 text-xs text-gray-400">
      <Icon name="network" className="w-4 h-4" />
      <span>
        {activeAgents.length === 0 ? 'Agents idle' : `${activeAgents.length} agent(s) working`}
      </span>
      {activeAgents.length > 0 && (
        <div className="flex gap-1">
          {activeAgents.map(agent => (
            <div key={agent} className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Tool Call Visualization

```typescript
interface ToolCallProps {
  toolCall: {
    name: string;
    args: any;
    status: 'running' | 'success' | 'error';
    result?: any;
  };
}

export const ToolCallDisplay: React.FC<ToolCallProps> = ({ toolCall }) => {
  return (
    <div className={`p-2 rounded text-xs ${
      toolCall.status === 'running' ? 'bg-yellow-900/30' :
      toolCall.status === 'success' ? 'bg-green-900/30' :
      'bg-red-900/30'
    }`}>
      <div className="flex items-center gap-2">
        <Icon name="tool" className="w-3 h-3" />
        <span className="font-mono">{toolCall.name}</span>
        {toolCall.status === 'running' && <Spinner className="w-3 h-3" />}
        {toolCall.status === 'success' && <Icon name="check" className="w-3 h-3 text-green-400" />}
        {toolCall.status === 'error' && <Icon name="x" className="w-3 h-3 text-red-400" />}
      </div>
      {toolCall.result && (
        <pre className="mt-1 text-xs text-gray-400 overflow-x-auto">
          {JSON.stringify(toolCall.result, null, 2)}
        </pre>
      )}
    </div>
  );
};
```

---

## 🔍 Context for Implementation

### Perplexity Searches

**Query 1: React Event Handling**
```
React hooks best practices for WebSocket events 2025:
- useEffect cleanup patterns
- Event listener lifecycle
- State updates from WebSocket
- Preventing memory leaks
- TypeScript event typing
```

**Query 2: Zustand Updates**
```
Zustand store updates from external events:
- Immer vs manual immutability
- Subscription patterns
- Performance optimization
- DevTools integration
- TypeScript best practices
```

### Exa Code Context

```typescript
await mcp1_get_code_context_exa({
  query: "React component WebSocket real-time updates TypeScript hooks",
  tokensNum: 5000
})
```

---

## ✅ Testing Checklist

- [ ] Toggle between Gemini and LangGraph modes
- [ ] Send message in LangGraph mode
- [ ] See agent attribution in messages
- [ ] Tool calls display correctly
- [ ] Assets appear in media panel
- [ ] Error handling works
- [ ] Reconnection after disconnect
- [ ] No memory leaks (check DevTools)

---

**Next:** Proceed to `Merge-04-Testing.md`
