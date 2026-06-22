from __future__ import annotations

from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    signup_url: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    api_docs: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    api_key: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        server_default=func.now(),
    )
