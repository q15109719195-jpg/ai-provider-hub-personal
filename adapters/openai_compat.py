from __future__ import annotations

import httpx

from adapters.base import BaseAdapter


class OpenAICompatAdapter(BaseAdapter):
    async def chat(self, model: str, messages: list[dict], **kwargs) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": model, "messages": messages}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError(f"provider error {response.status_code}: {response.text}")
        return response.json()["choices"][0]["message"]["content"]
