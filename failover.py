from __future__ import annotations

from collections import deque

import httpx

import crypto
from adapters.registry import PROVIDER_CONFIGS, get_adapter
from models import Provider
from router_logic import select_provider


FAILOVER_ERRORS = (httpx.TimeoutException,)


def _is_failover_runtime_error(exc: RuntimeError) -> bool:
    message = str(exc).lower()
    return "provider error 429" in message or "provider error 5" in message


async def chat_with_failover(
    task_type: str,
    message: str,
    model: str | None,
    providers: list[Provider],
) -> tuple[str, str, str]:
    if not providers:
        raise RuntimeError("all providers failed")

    preferred = select_provider(task_type, [provider.name for provider in providers])
    ordered = deque(providers)
    for index, provider in enumerate(providers):
        if provider.name.lower() == preferred:
            ordered.rotate(-index)
            break

    for provider in ordered:
        if provider.api_key is None or provider.api_key == "":
            continue

        try:
            api_key = crypto.decrypt(provider.api_key)
        except ValueError:
            continue

        try:
            adapter = get_adapter(provider.name.lower(), api_key)
        except ValueError:
            continue

        model_used = model or PROVIDER_CONFIGS.get(provider.name.lower(), {}).get("default_model", "default")

        try:
            content = await adapter.chat(model_used, [{"role": "user", "content": message}])
            return provider.name.lower(), model_used, content
        except RuntimeError as exc:
            if _is_failover_runtime_error(exc):
                continue
            continue
        except FAILOVER_ERRORS:
            continue

    raise RuntimeError("all providers failed")
