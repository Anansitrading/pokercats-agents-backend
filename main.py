"""
OpenCut AI Agent System - FastAPI Server
Multi-agent orchestration with LangGraph Supervisor Pattern
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Import routes
from routes import execute_router
from routes.voice import router as voice_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup: Initialize connections, load system agents, etc.
    print("🚀 Starting OpenCut Agent System...")
    
    # Optional startup validation (graceful handling if module missing)
    optimal_mode = True  # Assume optimal mode by default
    try:
        from agents.startup_validation import validate_and_report
        optimal_mode = validate_and_report(strict_mode=False)
        if not optimal_mode:
            print("⚠️  System running in degraded mode - see warnings above")
    except ImportError:
        print("⚠️  Startup validation module not found. Skipping dependency checks.")
    except Exception as e:
        print(f"⚠️  Startup validation failed: {e}")
        optimal_mode = False
    
    # Verify optional environment variables (for fallback/persistence)
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI fallback (not required if using Gemini)",
        "DATABASE_URL": "Persistence/checkpointing (not required for basic operation)",
    }
    
    missing_vars = [f"{var} ({desc})" for var, desc in optional_vars.items() if not os.getenv(var)]
    if missing_vars:
        print(f"ℹ️  Optional features disabled: {', '.join(missing_vars)}")
    
    print("✅ Agent System Ready")
    
    yield
    
    # Shutdown: Clean up resources
    print("🛑 Shutting down Agent System...")
    
    # Log final metrics
    from agents.observability import get_observability
    metrics = get_observability().get_degradation_metrics()
    print(f"📊 Session metrics: {metrics}")


# Create FastAPI app
app = FastAPI(
    title="OpenCut Agent System",
    description="Multi-agent orchestration for video editing powered by LangGraph",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS - Allow all origins for testing
# TODO: Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers for SSE
)


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint for monitoring and load balancers
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "opencut-agents",
            "version": "0.1.0",
        }
    )


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint with API information
    """
    return JSONResponse(
        content={
            "service": "OpenCut Agent System",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "execute": "/agents/execute/stream",
            }
        }
    )


# Include routers
app.include_router(execute_router, prefix="/agents/execute", tags=["execution"])
app.include_router(voice_router, prefix="/agents/voice", tags=["voice"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
