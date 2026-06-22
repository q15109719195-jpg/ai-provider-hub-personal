from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    @abstractmethod
    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError
