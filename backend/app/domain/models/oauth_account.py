from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

class OAuthAccount(BaseModel, TimestampedModel):
    """Модель для хранения данных об OAuth аккаунтах пользователей"""
    __tablename__ = "oauth_accounts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    access_token: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    token_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scopes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")
    
    # Ограничения и индексы
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_account"),
        Index("ix_oauth_provider_user", "provider", "provider_user_id"),
    )
    
    def __repr__(self) -> str:
        return f"<OAuthAccount {self.provider}:{self.provider_user_id}>"