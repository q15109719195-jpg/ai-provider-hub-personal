from __future__ import annotations


ROUTING_RULES = {
    "chat": ["openai", "groq", "deepseek"],
    "coding": ["deepseek", "openai", "anthropic"],
    "reasoning": ["anthropic", "openai", "deepseek"],
    "translate": ["deepseek", "openai", "groq"],
    "rewrite": ["openai", "anthropic", "deepseek"],
    "review": ["anthropic", "openai", "deepseek"],
}


def select_provider(task_type: str, enabled_providers: list[str]) -> str:
    if not enabled_providers:
        raise ValueError("no enabled providers available")

    enabled_set = {provider.lower() for provider in enabled_providers}
    candidates = ROUTING_RULES.get(task_type, ROUTING_RULES["chat"])
    for name in candidates:
        if name in enabled_set:
            return name
    return enabled_providers[0].lower()


def get_routing_rules() -> dict:
    return ROUTING_RULES.copy()
