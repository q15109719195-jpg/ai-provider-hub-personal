from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Provider
import failover


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
    try:
        provider_name, model, content = await failover.chat_with_failover(
            request.task_type, request.message, request.model, list(providers)
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return ChatResponse(provider=provider_name, model=model, content=content)
