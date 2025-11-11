# Merge-04: Testing & Validation

**Prerequisites:** Integration complete  
**Objective:** End-to-end testing of integrated system

---

## 🎯 Testing Strategy

Comprehensive testing across three layers:
1. **Unit Tests** - Individual services
2. **Integration Tests** - FastAPI ↔ Next.js communication
3. **End-to-End Tests** - Full user workflows

---

## 🧪 Unit Tests

### Test AgentBridgeService

**File:** `apps/web/src/services/__tests__/agent-bridge-service.test.ts`

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AgentBridgeService } from '../agent-bridge-service';
import { WebSocket as MockWebSocket } from 'mock-socket';

// Mock WebSocket
global.WebSocket = MockWebSocket as any;

describe('AgentBridgeService', () => {
  let service: AgentBridgeService;
  
  beforeEach(() => {
    service = new AgentBridgeService({
      apiUrl: 'http://localhost:8000',
      wsUrl: 'ws://localhost:8000',
      autoReconnect: false,
      reconnectDelay: 1000
    });
  });
  
  afterEach(() => {
    service.disconnect();
  });
  
  it('should connect to WebSocket', async () => {
    await expect(service.connect()).resolves.toBeUndefined();
    expect(service.isConnected()).toBe(true);
  });
  
  it('should send text message', async () => {
    await service.connect();
    
    expect(() => {
      service.sendMessage('Test message');
    }).not.toThrow();
  });
  
  it('should emit agent events', async () => {
    const mockEvent = {
      type: 'agent_message' as const,
      agent: 'test_agent',
      message: 'Test response'
    };
    
    const handler = vi.fn();
    service.on('agent_message', handler);
    
    await service.connect();
    
    // Simulate incoming message
    service['handleAgentEvent'](mockEvent);
    
    expect(handler).toHaveBeenCalledWith(mockEvent);
  });
  
  it('should handle disconnection', async () => {
    await service.connect();
    
    const handler = vi.fn();
    service.on('disconnected', handler);
    
    service.disconnect();
    
    expect(service.isConnected()).toBe(false);
  });
});
```

### Test FastAPI WebSocket

**File:** `apps/agents/tests/test_voice_websocket.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_websocket_connection(client):
    """Test WebSocket connection establishment"""
    with client.websocket_connect("/agents/voice/stream") as websocket:
        # Connection should succeed
        assert websocket is not None

def test_websocket_message_handling(client):
    """Test message handling"""
    with client.websocket_connect("/agents/voice/stream") as websocket:
        # Send test message
        websocket.send_json({
            "type": "message",
            "message": "Test message",
            "context": {}
        })
        
        # Expect agent_started event
        data = websocket.receive_json()
        assert data["type"] == "agent_started"
        assert "agent" in data
        
        # Expect completion eventually
        # (simplified - actual test would wait for events)

def test_websocket_error_handling(client):
    """Test error handling"""
    with client.websocket_connect("/agents/voice/stream") as websocket:
        # Send invalid message
        websocket.send_json({
            "type": "invalid_type"
        })
        
        # Expect error event
        data = websocket.receive_json()
        assert data["type"] == "error"
```

---

## 🔗 Integration Tests

### Test Full Communication Flow

**File:** `apps/web/src/__tests__/integration/agent-flow.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RightPanel } from '@/components/kijko-agent/RightPanel';
import { getAgentBridge } from '@/services/agent-bridge-service';

// Mock agent bridge
vi.mock('@/services/agent-bridge-service');

describe('Agent Integration Flow', () => {
  beforeEach(() => {
    const mockBridge = {
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn(),
      sendMessage: vi.fn(),
      on: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true)
    };
    
    (getAgentBridge as any).mockReturnValue(mockBridge);
  });
  
  it('should send message to LangGraph agents', async () => {
    const user = userEvent.setup();
    
    render(<RightPanel /* props */ />);
    
    // Switch to LangGraph mode
    const modeSelect = screen.getByLabelText(/agent mode/i);
    await user.selectOptions(modeSelect, 'langgraph');
    
    // Type message
    const input = screen.getByPlaceholderText(/type your prompt/i);
    await user.type(input, 'Create a product demo video');
    
    // Submit
    const submitBtn = screen.getByRole('button', { name: /send/i });
    await user.click(submitBtn);
    
    // Verify message sent to bridge
    const bridge = getAgentBridge();
    expect(bridge.sendMessage).toHaveBeenCalledWith(
      'Create a product demo video',
      expect.any(Object)
    );
  });
  
  it('should display agent responses', async () => {
    render(<RightPanel /* props */ />);
    
    const bridge = getAgentBridge();
    const messageHandler = (bridge.on as any).mock.calls.find(
      call => call[0] === 'agent_message'
    )?.[1];
    
    // Simulate agent message
    messageHandler({
      type: 'agent_message',
      agent: 'vrd_agent',
      message: 'Analyzing your requirements...'
    });
    
    // Verify message displayed
    await waitFor(() => {
      expect(screen.getByText(/analyzing your requirements/i)).toBeInTheDocument();
      expect(screen.getByText(/vrd_agent/i)).toBeInTheDocument();
    });
  });
});
```

---

## 🎭 End-to-End Tests

### Test Full User Workflow

**File:** `apps/web/e2e/agent-integration.spec.ts` (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('LangGraph Agent Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Start both servers (Next.js and FastAPI)
    // This assumes docker-compose or concurrent npm scripts
    await page.goto('http://localhost:3000');
  });
  
  test('should create video using LangGraph agents', async ({ page }) => {
    // 1. Switch to LangGraph mode
    await page.selectOption('[data-testid="agent-mode-select"]', 'langgraph');
    
    // 2. Type prompt
    await page.fill('[data-testid="chat-input"]', 'Create a 30-second product demo video for a SaaS tool');
    
    // 3. Submit
    await page.click('[data-testid="chat-submit"]');
    
    // 4. Wait for VRD agent response
    await expect(page.locator('text=vrd_agent')).toBeVisible({ timeout: 10000 });
    
    // 5. Wait for agent to finish
    await expect(page.locator('text=All agents completed')).toBeVisible({ timeout: 60000 });
    
    // 6. Verify asset generated
    await expect(page.locator('[data-testid="media-panel"]')).toContainText('Generated');
    
    // 7. Verify asset draggable to timeline
    const asset = page.locator('[data-testid="media-item"]').first();
    const timeline = page.locator('[data-testid="timeline"]');
    
    await asset.dragTo(timeline);
    
    // 8. Verify clip added to timeline
    await expect(timeline.locator('[data-testid="timeline-clip"]')).toHaveCount(1);
  });
  
  test('should handle agent errors gracefully', async ({ page }) => {
    // Simulate agent failure
    // (Would require mocking or error injection)
    
    await page.selectOption('[data-testid="agent-mode-select"]', 'langgraph');
    await page.fill('[data-testid="chat-input"]', 'Invalid request');
    await page.click('[data-testid="chat-submit"]');
    
    // Verify error message displayed
    await expect(page.locator('text=Error from')).toBeVisible({ timeout: 5000 });
    
    // Verify user can still interact
    await page.fill('[data-testid="chat-input"]', 'Valid request');
    await expect(page.locator('[data-testid="chat-submit"]')).toBeEnabled();
  });
  
  test('should fallback to Gemini if agents unavailable', async ({ page }) => {
    // Stop FastAPI server to simulate unavailability
    // (Would require test orchestration)
    
    await page.selectOption('[data-testid="agent-mode-select"]', 'langgraph');
    
    // Verify fallback message
    await expect(page.locator('text=Failed to connect to LangGraph agents')).toBeVisible();
    
    // Verify mode switched back to Gemini
    await expect(page.locator('[data-testid="agent-mode-select"]')).toHaveValue('gemini');
  });
});
```

---

## 🚀 Performance Tests

### Load Testing

**File:** `apps/agents/tests/load_test.py`

```python
import asyncio
import websockets
import json
import time
from statistics import mean, stdev

async def test_single_connection():
    """Test single WebSocket connection latency"""
    uri = "ws://localhost:8000/agents/voice/stream"
    
    start = time.time()
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "type": "message",
            "message": "Test message"
        }))
        
        # Wait for completion
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "completed":
                break
    
    return time.time() - start

async def load_test(num_connections=10):
    """Test multiple concurrent connections"""
    latencies = await asyncio.gather(*[
        test_single_connection()
        for _ in range(num_connections)
    ])
    
    print(f"Concurrent connections: {num_connections}")
    print(f"Mean latency: {mean(latencies):.2f}s")
    print(f"Std dev: {stdev(latencies):.2f}s")
    print(f"Min: {min(latencies):.2f}s")
    print(f"Max: {max(latencies):.2f}s")

if __name__ == "__main__":
    asyncio.run(load_test(10))
```

---

## 📊 Success Criteria

### Functional Requirements
- [ ] User can switch between Gemini and LangGraph modes
- [ ] Messages sent to correct system
- [ ] Agent responses display correctly
- [ ] Tool calls visible in UI
- [ ] Assets appear in media panel
- [ ] Assets draggable to timeline
- [ ] Error handling works
- [ ] Fallback to Gemini when agents unavailable

### Performance Requirements
- [ ] WebSocket connection < 100ms
- [ ] Message latency < 500ms
- [ ] Agent response starts streaming < 2s
- [ ] No memory leaks during 10 min session
- [ ] Supports 10 concurrent connections

### Quality Requirements
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] TypeScript compiles without errors
- [ ] No console errors in browser
- [ ] Observability logs capture all events

---

## 🔍 Context for Implementation

### Perplexity Searches

**Query 1: Testing Strategies**
```
React testing library best practices 2025:
- WebSocket mocking strategies
- Async event testing
- User event simulation
- Integration test patterns
- E2E testing with Playwright
```

**Query 2: Performance Testing**
```
WebSocket performance testing Python:
- Load testing tools
- Latency measurement
- Concurrent connections
- Resource monitoring
- Benchmarking best practices
```

---

**Next:** Proceed to `Merge-05-Deployment.md`
