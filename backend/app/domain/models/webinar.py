# backend/app/domain/models/webinar.py
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

# Перечисления для вебинаров
class WebinarStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"  # Запланирован
    LIVE = "LIVE"           # Идет сейчас
    ENDED = "ENDED"         # Завершен
    CANCELLED = "CANCELLED" # Отменен

class ParticipantRole(str, enum.Enum):
    HOST = "HOST"           # Ведущий (создатель)
    MODERATOR = "MODERATOR" # Модератор
    PARTICIPANT = "PARTICIPANT" # Участник

class Webinar(BaseModel, TimestampedModel):
    """Модель вебинара"""
    __tablename__ = "webinars"

    # Основная информация
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Ведущий (только admin или plant_expert)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Jitsi конфигурация
    room_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Расписание
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    
    # Настройки
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[WebinarStatus] = mapped_column(Enum(WebinarStatus), default=WebinarStatus.SCHEDULED)
    
    # Связь с растениями (опционально)
    plant_topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plants.id"), nullable=True)
    
    # Jitsi конфигурация (JSON)
    jitsi_room_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Отношения
    host: Mapped["User"] = relationship("User", foreign_keys=[host_id])
    plant_topic: Mapped[Optional["Plant"]] = relationship("Plant", foreign_keys=[plant_topic_id])
    participants: Mapped[List["WebinarParticipant"]] = relationship(
        "WebinarParticipant", back_populates="webinar", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Webinar {self.title} ({self.status.value})>"

class WebinarParticipant(BaseModel, TimestampedModel):
    """Модель участника вебинара"""
    __tablename__ = "webinar_participants"

    # Связи
    webinar_id: Mapped[int] = mapped_column(ForeignKey("webinars.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Роль участника
    role: Mapped[ParticipantRole] = mapped_column(Enum(ParticipantRole), default=ParticipantRole.PARTICIPANT)
    
    # Время участия
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    left_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Отношения
    webinar: Mapped["Webinar"] = relationship("Webinar", back_populates="participants")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<WebinarParticipant {self.user_id} in {self.webinar_id} ({self.role.value})>"

    # Уникальность: один пользователь может быть участником вебинара только один раз
    __table_args__ = (
        {"extend_existing": True}
    )
