from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

class Answer(BaseModel, TimestampedModel):
    """Модель ответа на вопрос"""
    __tablename__ = "answers"

    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    votes_up: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    votes_down: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Отношения
    author: Mapped["User"] = relationship("User", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers") 