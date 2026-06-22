from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderBase(BaseModel):
    name: str
    website: str | None = None
    signup_url: str | None = None
    api_docs: str | None = None
    api_key: str | None = None
    enabled: bool = True


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    signup_url: str | None = None
    api_docs: str | None = None
    api_key: str | None = None
    enabled: bool | None = None


class ProviderOut(ProviderBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
