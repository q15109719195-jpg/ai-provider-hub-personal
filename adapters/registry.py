from __future__ import annotations

from adapters.anthropic import AnthropicAdapter
from adapters.base import BaseAdapter
from adapters.openai_compat import OpenAICompatAdapter


PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "adapter_type": "openai_compat",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "default_model": "claude-haiku-4-5-20251001",
        "adapter_type": "anthropic",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "adapter_type": "openai_compat",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama3-8b-8192",
        "adapter_type": "openai_compat",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openai/gpt-4o-mini",
        "adapter_type": "openai_compat",
    },
}


def get_adapter(provider_name: str, api_key: str) -> BaseAdapter:
    config = PROVIDER_CONFIGS.get(provider_name.lower())
    if config is None:
        raise ValueError(f"unknown provider: {provider_name}")
    if config["adapter_type"] == "anthropic":
        return AnthropicAdapter(api_key)
    return OpenAICompatAdapter(config["base_url"], api_key)
