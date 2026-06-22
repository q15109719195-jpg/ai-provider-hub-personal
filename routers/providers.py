from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

import crypto

from database import get_db
from models import Provider
from schemas import ProviderCreate, ProviderOut, ProviderUpdate


router = APIRouter(prefix="/providers", tags=["providers"])


def _provider_or_404(db: Session, provider_id: int) -> Provider:
    provider = db.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return provider


def _name_exists(db: Session, name: str, exclude_id: int | None = None) -> bool:
    stmt = select(Provider).where(Provider.name == name)
    if exclude_id is not None:
        stmt = stmt.where(Provider.id != exclude_id)
    return db.scalar(stmt) is not None


def _decrypt_provider(provider: Provider) -> Provider:
    if provider.api_key is not None:
        provider.api_key = crypto.decrypt(provider.api_key)
    return provider


@router.get("", response_model=list[ProviderOut])
def list_providers(db: Session = Depends(get_db)):
    providers = db.scalars(select(Provider).order_by(Provider.id)).all()
    return [_decrypt_provider(provider) for provider in providers]


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
def create_provider(payload: ProviderCreate, db: Session = Depends(get_db)):
    if _name_exists(db, payload.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider name already exists")

    provider = Provider(
        name=payload.name,
        website=payload.website,
        signup_url=payload.signup_url,
        api_docs=payload.api_docs,
        api_key=crypto.encrypt(payload.api_key) if payload.api_key is not None else None,
        enabled=payload.enabled,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return _decrypt_provider(provider)


@router.get("/{provider_id}", response_model=ProviderOut)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    return _decrypt_provider(_provider_or_404(db, provider_id))


@router.put("/{provider_id}", response_model=ProviderOut)
def update_provider(provider_id: int, payload: ProviderUpdate, db: Session = Depends(get_db)):
    provider = _provider_or_404(db, provider_id)

    if payload.name is not None and payload.name != provider.name and _name_exists(db, payload.name, exclude_id=provider_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider name already exists")

    data = payload.model_dump(exclude_unset=True)
    if "api_key" in data and data["api_key"] is not None:
        data["api_key"] = crypto.encrypt(data["api_key"])
    for field, value in data.items():
        setattr(provider, field, value)

    db.commit()
    db.refresh(provider)
    return _decrypt_provider(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = _provider_or_404(db, provider_id)
    db.delete(provider)
    db.commit()
    return None
