# OpenCut Agent System

Multi-agent orchestration system powered by LangGraph for video production workflows.

## Architecture

The system uses a **Supervisor Pattern** with specialized sub-agents:

1. **Supervisor**: Orchestrates workflow and routes tasks to appropriate agents
2. **VRD (Video Requirements Detective)**: Analyzes requirements and defines scope
3. **ScriptSmith**: Writes video scripts and narratives
4. **ShotMaster**: Designs storyboards and visual sequences
5. **VideoSolver**: Plans production logistics and technical requirements

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL with pgvector extension
- OpenAI API key

### Installation

1. Install dependencies:
```bash
cd apps/agents
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Verify PostgreSQL connection:
```bash
psql $DATABASE_URL -c "SELECT 1;"
```

### Running the Server

Development mode with auto-reload:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Execute Agent (Streaming)
```bash
POST /agents/execute/stream
Content-Type: application/json

{
  "message": "Create a 30-second product demo video",
  "thread_id": "optional-thread-id",
  "user_context": {}
}
```

Response: Server-Sent Events (SSE) stream

Event types:
- `start`: Execution started
- `token`: Individual LLM token
- `message`: Complete agent message
- `tool_call`: Agent called a tool
- `tool_start`: Tool execution started
- `tool_end`: Tool execution completed
- `agent_switch`: Switched to different agent
- `error`: Error occurred
- `done`: Execution completed

### Execute Agent (Non-streaming)
```bash
POST /agents/execute/invoke
Content-Type: application/json

{
  "message": "Create a script for a product video",
  "thread_id": "optional-thread-id"
}
```

Response: Complete execution result

### Get Thread History
```bash
GET /agents/execute/threads/{thread_id}
```

## Testing

### Manual Testing

Test streaming endpoint:
```bash
curl -N -H "Content-Type: application/json" \
  -d '{"message":"Create a 30-second video script"}' \
  http://localhost:8000/agents/execute/stream
```

Test invoke endpoint:
```bash
curl -X POST http://localhost:8000/agents/execute/invoke \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the steps to create a video?"}'
```

### Integration with Frontend

```typescript
// Example: Consuming SSE stream in TypeScript
const eventSource = new EventSource('/agents/execute/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Create a video' })
});

eventSource.addEventListener('token', (event) => {
  const data = JSON.parse(event.data);
  console.log('Token:', data.token);
});

eventSource.addEventListener('done', (event) => {
  console.log('Execution complete');
  eventSource.close();
});
```

## Project Structure

```
apps/agents/
├── agents/
│   ├── __init__.py
│   ├── supervisor.py       # LangGraph supervisor
│   └── sub_agents.py       # Specialized sub-agents
├── routes/
│   ├── __init__.py
│   └── execute.py          # Execution endpoints
├── tools/                  # (Future) External API tools
├── middleware/             # (Future) Custom middleware
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
└── README.md              # This file
```

## Development

### Adding New Agents

1. Create agent in `agents/sub_agents.py`:
```python
def create_my_agent(model: BaseChatModel):
    tools = [my_tool_function]
    return create_react_agent(
        model=model,
        tools=tools,
        name="my_agent",
        prompt="Agent instructions..."
    )
```

2. Register in supervisor (`agents/supervisor.py`):
```python
my_agent = create_my_agent(model)
supervisor = create_supervisor(
    agents=[..., my_agent],
    # ...
)
```

### Adding New Tools

Create tool functions in `agents/sub_agents.py` or `tools/`:
```python
def my_tool(input: str) -> str:
    """
    Tool description for LLM
    
    Args:
        input: Input parameter
        
    Returns:
        Tool result
    """
    # Implementation
    return result
```

## Monitoring

### Langfuse Integration

Set up Langfuse environment variables to enable tracing:
```bash
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

View traces at: https://cloud.langfuse.com

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the agents directory
cd apps/agents

# Run as module
python -m main
```

### Database Connection
```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT version();"

# Check pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Environment Variables
```bash
# Check loaded variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

## Sprint 2 Deliverables

✅ **Task 2.1**: FastAPI server with CORS and health checks
✅ **Task 2.2**: LangGraph Supervisor with StateGraph
✅ **Task 2.3**: 4 specialized sub-agents (VRD, ScriptSmith, ShotMaster, VideoSolver)
✅ **Task 2.4**: Streaming API with Server-Sent Events

## Next Steps (Sprint 3)

- Integrate external APIs (fal.ai, Freepik, OpenAI image generation)
- Add tool registry with semantic search
- Implement MCP tool integration
- Add Redis caching for tool results

## License

See main repository LICENSE file.
