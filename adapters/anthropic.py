from __future__ import annotations

import httpx

from adapters.base import BaseAdapter


class AnthropicAdapter(BaseAdapter):
    def __init__(self, api_key: str):
        super().__init__("https://api.anthropic.com", api_key)

    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {"model": model, "max_tokens": 1024, "messages": messages}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError(f"provider error {response.status_code}: {response.text}")
        return response.json()["content"][0]["text"]
