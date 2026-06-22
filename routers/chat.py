from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

import crypto
from adapters.registry import PROVIDER_CONFIGS, get_adapter
from database import get_db
from models import Provider
from router_logic import select_provider


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    task_type: str = "chat"
    model: str | None = None


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    providers = db.scalars(select(Provider).where(Provider.enabled.is_(True)).order_by(Provider.id)).all()
    if not providers:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no enabled providers available")

    provider_name = select_provider(request.task_type, [provider.name for provider in providers])
    provider = next((item for item in providers if item.name.lower() == provider_name), None)
    if provider is None:
        provider = providers[0]
        provider_name = provider.name.lower()

    if provider.api_key is None or provider.api_key == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"provider {provider.name} has no api_key configured")

    try:
        api_key = crypto.decrypt(provider.api_key)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"provider {provider.name} has no api_key configured")

    adapter = get_adapter(provider_name, api_key)
    model = request.model or PROVIDER_CONFIGS[provider_name]["default_model"]
    messages = [{"role": "user", "content": request.message}]
    content = await adapter.chat(model, messages)
    return ChatResponse(provider=provider_name, model=model, content=content)
