from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from router_logic import select_provider


def test_select_provider_chat_prefers_openai():
    assert select_provider("chat", ["openai", "groq"]) == "openai"


def test_select_provider_coding_prefers_deepseek():
    assert select_provider("coding", ["groq", "deepseek"]) == "deepseek"


def test_select_provider_reasoning_falls_back_to_first_enabled():
    assert select_provider("reasoning", ["groq"]) == "groq"


def test_select_provider_empty_enabled_raises():
    with pytest.raises(ValueError):
        select_provider("chat", [])


def test_select_provider_unknown_task_falls_back_to_chat_rules():
    assert select_provider("unknown", ["openai", "groq"]) == "openai"
