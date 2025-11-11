"""
Model Factory for LLM Selection
Supports OpenAI and Google Gemini models with per-task optimization
"""

import os
from typing import Literal
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


TaskType = Literal["reasoning", "repetitive", "creative"]
Provider = Literal["openai", "google"]


def get_model(
    provider: Provider = "google",
    task_type: TaskType = "reasoning",
    temperature: float = 0.7,
    streaming: bool = False
) -> BaseChatModel:
    """
    Get optimized LLM model based on provider and task type
    
    Args:
        provider: "openai" or "google"
        task_type: "reasoning" (complex analysis), "repetitive" (simple tasks), "creative" (generation)
        temperature: Model temperature (0.0-1.0)
        streaming: Enable streaming responses
        
    Returns:
        Configured BaseChatModel instance
    
    Examples:
        # Gemini Pro for complex reasoning
        supervisor_model = get_model(provider="google", task_type="reasoning")
        
        # Gemini Flash for simple tasks
        simple_model = get_model(provider="google", task_type="repetitive")
        
        # OpenAI GPT-4 fallback
        openai_model = get_model(provider="openai", task_type="reasoning")
    """
    if provider == "google":
        return _get_gemini_model(task_type, temperature, streaming)
    elif provider == "openai":
        return _get_openai_model(task_type, temperature, streaming)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def _get_gemini_model(
    task_type: TaskType,
    temperature: float,
    streaming: bool
) -> ChatGoogleGenerativeAI:
    """Get Google Gemini model based on task type"""
    
    # Model selection based on task complexity - USING GEMINI 2.5 (verified from API)
    if task_type == "reasoning":
        model_name = "gemini-2.5-pro"  # Latest Pro model for complex reasoning
    elif task_type == "repetitive":
        model_name = "gemini-2.5-flash"  # Fast, cost-effective
    elif task_type == "creative":
        model_name = "gemini-2.5-pro"  # Best for creative tasks
    else:
        model_name = "gemini-2.5-flash"
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=temperature,
        streaming=streaming,
        convert_system_message_to_human=True,  # Gemini compatibility
    )


def _get_openai_model(
    task_type: TaskType,
    temperature: float,
    streaming: bool
) -> ChatOpenAI:
    """Get OpenAI model based on task type"""
    
    # Model selection based on task complexity
    if task_type == "reasoning":
        model_name = "gpt-4o"  # Best reasoning
    elif task_type == "repetitive":
        model_name = "gpt-4o-mini"  # Fast, cheaper
    elif task_type == "creative":
        model_name = "gpt-4o"  # Best for creative tasks
    else:
        model_name = "gpt-4o-mini"
    
    return ChatOpenAI(
        model=model_name,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=temperature,
        streaming=streaming,
    )


# Per-agent model recommendations based on role
AGENT_MODEL_CONFIG = {
    "supervisor": {
        "task_type": "repetitive",  # Use Flash to avoid rate limits
        "temperature": 0.7,
    },
    "vrd_agent": {
        "task_type": "repetitive",  # Use Flash for speed
        "temperature": 0.7,
    },
    "script_smith_agent": {
        "task_type": "repetitive",  # Use Flash - still creative with higher temp
        "temperature": 0.9,
    },
    "shot_master_agent": {
        "task_type": "repetitive",  # Use Flash for speed
        "temperature": 0.7,
    },
    "video_solver_agent": {
        "task_type": "repetitive",  # Use Flash
        "temperature": 0.5,
    },
}


def get_agent_model(
    agent_name: str,
    provider: Provider = "google"
) -> BaseChatModel:
    """
    Get optimized model for specific agent
    
    Args:
        agent_name: Name of agent (supervisor, vrd_agent, etc.)
        provider: Model provider to use
        
    Returns:
        Configured model optimized for agent's task
        
    Example:
        # Get optimized model for ScriptSmith (creative task)
        model = get_agent_model("script_smith_agent", provider="google")
        # → Returns gemini-2.5-pro with temperature=0.9
    """
    config = AGENT_MODEL_CONFIG.get(
        agent_name,
        {"task_type": "reasoning", "temperature": 0.7}
    )
    
    return get_model(
        provider=provider,
        task_type=config["task_type"],
        temperature=config["temperature"]
    )


def get_model_info(provider: Provider, task_type: TaskType) -> dict:
    """
    Get information about model selection
    
    Useful for logging and debugging
    """
    if provider == "google":
        model_map = {
            "reasoning": "gemini-2.5-pro",
            "repetitive": "gemini-2.5-flash",
            "creative": "gemini-2.5-pro",
        }
        model_name = model_map.get(task_type, "gemini-2.5-flash")
        cost_per_1k = {
            "gemini-2.5-pro": 0.00125,  # $1.25 per 1M tokens
            "gemini-2.5-flash": 0.000075,  # $0.075 per 1M tokens
        }
    else:  # openai
        model_map = {
            "reasoning": "gpt-4o",
            "repetitive": "gpt-4o-mini",
            "creative": "gpt-4o",
        }
        model_name = model_map.get(task_type, "gpt-4o-mini")
        cost_per_1k = {
            "gpt-4o": 0.0025,  # Input: $2.50 per 1M tokens
            "gpt-4o-mini": 0.00015,  # Input: $0.15 per 1M tokens
        }
    
    return {
        "provider": provider,
        "task_type": task_type,
        "model_name": model_name,
        "cost_per_1k_tokens": cost_per_1k.get(model_name, 0.0),
    }
