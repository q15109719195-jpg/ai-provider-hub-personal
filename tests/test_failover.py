from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import crypto
from failover import chat_with_failover


@pytest.fixture
def providers():
    provider1 = MagicMock()
    provider1.name = "OpenAI"
    provider1.api_key = crypto.encrypt("key1")
    provider1.enabled = True

    provider2 = MagicMock()
    provider2.name = "Groq"
    provider2.api_key = crypto.encrypt("key2")
    provider2.enabled = True

    provider3 = MagicMock()
    provider3.name = "Anthropic"
    provider3.api_key = crypto.encrypt("key3")
    provider3.enabled = True

    return [provider1, provider2, provider3]


def test_failover_succeeds_on_first_provider(providers):
    adapter = SimpleNamespace(chat=AsyncMock(return_value="ok"))
    with patch("failover.get_adapter", return_value=adapter):
        provider_name, model, content = asyncio.run(chat_with_failover("chat", "hello", None, providers))
    assert provider_name == "openai"
    assert content == "ok"
    assert model == "gpt-4o-mini"


def test_failover_skips_429_and_uses_second(providers):
    first = SimpleNamespace(chat=AsyncMock(side_effect=RuntimeError("provider error 429: rate limited")))
    second = SimpleNamespace(chat=AsyncMock(return_value="fallback"))
    third = SimpleNamespace(chat=AsyncMock(return_value="unused"))

    def fake_get_adapter(name, api_key):
        if name == "openai":
            return first
        if name == "groq":
            return second
        return third

    with patch("failover.get_adapter", side_effect=fake_get_adapter):
        provider_name, model, content = asyncio.run(chat_with_failover("chat", "hello", None, providers))
    assert provider_name == "groq"
    assert content == "fallback"


def test_failover_skips_provider_with_no_key(providers):
    providers[0].api_key = None
    adapter = SimpleNamespace(chat=AsyncMock(return_value="ok"))

    with patch("failover.get_adapter", return_value=adapter):
        provider_name, model, content = asyncio.run(chat_with_failover("chat", "hello", None, providers))
    assert provider_name == "groq"
    assert content == "ok"


def test_failover_all_fail_raises_runtime_error(providers):
    failing = SimpleNamespace(chat=AsyncMock(side_effect=RuntimeError("provider error 500: boom")))
    with patch("failover.get_adapter", return_value=failing):
        with pytest.raises(RuntimeError, match="all providers failed"):
            asyncio.run(chat_with_failover("chat", "hello", None, providers))
