from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

class Question(BaseModel, TimestampedModel):
    """Модель вопроса пользователя"""
    __tablename__ = "questions"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    votes_up: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    votes_down: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    plant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plants.id"), nullable=True)

    # Отношения
    author: Mapped["User"] = relationship("User", back_populates="questions")
    answers: Mapped[List["Answer"]] = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )
    plant: Mapped[Optional["Plant"]] = relationship("Plant", back_populates="questions")