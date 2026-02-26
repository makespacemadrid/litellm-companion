"""
Free-tier provider presets for quick setup.

Based on research of free LLM API providers in 2025.
Sources:
- https://github.com/cheahjs/free-llm-api-resources
- https://apidog.com/blog/free-open-source-llm-apis/
- https://madappgang.com/blog/best-free-ai-apis-for-2025-build-with-llms-without/
"""

from typing import TypedDict


class ProviderPreset(TypedDict):
    """Provider configuration preset."""
    name: str
    base_url: str
    type: str  # 'ollama', 'openai', or 'compat'
    default_ollama_mode: str | None
    model_filter: str | None
    description: str
    notes: str
    limits: str
    api_key_required: bool
    api_key_url: str | None
    sync_interval_seconds: int


# Free tier provider presets
FREE_TIER_PRESETS: list[ProviderPreset] = [
    {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Ultra-fast inference with Llama, Mixtral, Gemma models",
        "notes": "Leading speed (300+ tokens/sec), 14,400 req/day free tier",
        "limits": "14,400 requests/day",
        "api_key_required": True,
        "api_key_url": "https://console.groq.com/keys",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "OpenRouter Free",
        "base_url": "https://openrouter.ai/api/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": ":free",  # Filter to only free models
        "description": "30+ free models aggregator (Llama, Gemma, Phi, etc.)",
        "notes": "Best for experimentation, no credit card required",
        "limits": "Varies by model, generous free tier",
        "api_key_required": True,
        "api_key_url": "https://openrouter.ai/keys",
        "sync_interval_seconds": 7200,  # 2 hours
    },
    {
        "name": "SambaNova Cloud",
        "base_url": "https://api.sambanova.ai/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Fast inference endpoint with a documented free tier",
        "notes": "OpenAI-compatible API and rate limits published by model",
        "limits": "Free tier with model-specific rate limits",
        "api_key_required": True,
        "api_key_url": "https://cloud.sambanova.ai/apis",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Gemini models via OpenAI-compatible endpoint",
        "notes": "Free usage tier available for selected models in AI Studio pricing",
        "limits": "Free tier (model dependent)",
        "api_key_required": True,
        "api_key_url": "https://aistudio.google.com/app/apikey",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Cerebras",
        "base_url": "https://api.cerebras.ai/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Fastest token generation (Llama 3.3 70B free)",
        "notes": "Industry-leading speed, 8K context limit on free tier",
        "limits": "Free tier with usage limits",
        "api_key_required": True,
        "api_key_url": "https://cloud.cerebras.ai/",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Mistral AI",
        "base_url": "https://api.mistral.ai/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Mistral models with 1 billion tokens/month free",
        "notes": "European AI leader, generous free tier",
        "limits": "1 billion tokens/month",
        "api_key_required": True,
        "api_key_url": "https://console.mistral.ai/api-keys/",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Hugging Face",
        "base_url": "https://router.huggingface.co",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Free inference API for thousands of models",
        "notes": "Rate-limited, best for testing and small projects",
        "limits": "Rate-limited free tier",
        "api_key_required": True,
        "api_key_url": "https://huggingface.co/settings/tokens",
        "sync_interval_seconds": 7200,  # 2 hours
    },
    {
        "name": "DeepInfra",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Fast inference for popular open-source models",
        "notes": "Free tier available, good performance",
        "limits": "Free tier with usage limits",
        "api_key_required": True,
        "api_key_url": "https://deepinfra.com/dash/api_keys",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Fireworks AI",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "type": "openai",
        "default_ollama_mode": None,
        "model_filter": None,
        "description": "Production-ready inference for open models",
        "notes": "Free credits available, enterprise-grade",
        "limits": "Free credits on signup",
        "api_key_required": True,
        "api_key_url": "https://fireworks.ai/api-keys",
        "sync_interval_seconds": 3600,  # 1 hour
    },
    {
        "name": "Ollama Cloud",
        "base_url": "https://ollama.com",
        "type": "ollama",
        "default_ollama_mode": "openai",
        "model_filter": None,
        "description": "Cloud-hosted Ollama models (recently launched)",
        "notes": "Free tier available, familiar Ollama interface",
        "limits": "Free tier with usage limits",
        "api_key_required": True,
        "api_key_url": "https://ollama.com/settings/keys",
        "sync_interval_seconds": 7200,  # 2 hours
    },
]


def get_preset_by_name(name: str) -> ProviderPreset | None:
    """Get a preset by name (case-insensitive)."""
    name_lower = name.lower()
    for preset in FREE_TIER_PRESETS:
        if preset["name"].lower() == name_lower:
            return preset
    return None


def list_presets() -> list[dict]:
    """List all available presets with complete info for UI."""
    return [
        {
            "name": preset["name"],
            "base_url": preset["base_url"],
            "type": preset["type"],
            "model_filter": preset["model_filter"],
            "description": preset["description"],
            "limits": preset["limits"],
            "api_key_required": preset["api_key_required"],
            "api_key_url": preset["api_key_url"],
            "sync_interval_seconds": preset["sync_interval_seconds"],
        }
        for preset in FREE_TIER_PRESETS
    ]
