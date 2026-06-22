from __future__ import annotations

from pathlib import Path
import asyncio
import sys

import httpx
import respx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adapters.anthropic import AnthropicAdapter
from adapters.openai_compat import OpenAICompatAdapter


def test_openai_compat_chat():
    adapter = OpenAICompatAdapter("https://api.openai.com/v1", "test-key")
    with respx.mock(assert_all_called=True, base_url="https://api.openai.com/v1") as mock:
        mock.post("/chat/completions").respond(
            200,
            json={"choices": [{"message": {"content": "hello"}}]},
        )
        original = httpx.AsyncClient
        httpx.AsyncClient = lambda timeout=30: original(transport=respx.transports.MockTransport(router=mock), timeout=timeout)
        try:
            result = asyncio.run(adapter.chat("gpt-4o-mini", [{"role": "user", "content": "hi"}]))
        finally:
            httpx.AsyncClient = original
    assert result == "hello"


def test_anthropic_chat():
    adapter = AnthropicAdapter("test-key")
    with respx.mock(assert_all_called=True, base_url="https://api.anthropic.com") as mock:
        mock.post("/v1/messages").respond(
            200,
            json={"content": [{"text": "world"}]},
        )
        original = httpx.AsyncClient
        httpx.AsyncClient = lambda timeout=30: original(transport=respx.transports.MockTransport(router=mock), timeout=timeout)
        try:
            result = asyncio.run(adapter.chat("claude-haiku-4-5-20251001", [{"role": "user", "content": "hi"}]))
        finally:
            httpx.AsyncClient = original
    assert result == "world"


def test_openai_compat_error():
    adapter = OpenAICompatAdapter("https://api.openai.com/v1", "test-key")
    with respx.mock(assert_all_called=True, base_url="https://api.openai.com/v1") as mock:
        mock.post("/chat/completions").respond(500, text="boom")
        original = httpx.AsyncClient
        httpx.AsyncClient = lambda timeout=30: original(transport=respx.transports.MockTransport(router=mock), timeout=timeout)
        try:
            asyncio.run(adapter.chat("gpt-4o-mini", [{"role": "user", "content": "hi"}]))
            assert False, "expected RuntimeError"
        except RuntimeError as exc:
            assert "provider error 500" in str(exc)
        finally:
            httpx.AsyncClient = original
