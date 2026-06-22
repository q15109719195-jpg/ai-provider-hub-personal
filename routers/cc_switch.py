from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Provider
from router_logic import get_routing_rules


router = APIRouter(prefix="/cc-switch", tags=["cc-switch"])


class CCProviderItem(BaseModel):
    id: int
    name: str
    website: str | None
    enabled: bool
    has_key: bool

    model_config = ConfigDict(from_attributes=False)


@router.get("/providers", response_model=list[CCProviderItem])
def list_cc_providers(db: Session = Depends(get_db)):
    providers = db.scalars(select(Provider).order_by(Provider.id)).all()
    return [
        CCProviderItem(
            id=provider.id,
            name=provider.name,
            website=provider.website,
            enabled=provider.enabled,
            has_key=bool(provider.api_key),
        )
        for provider in providers
    ]


@router.get("/router")
def get_cc_router():
    return get_routing_rules()
