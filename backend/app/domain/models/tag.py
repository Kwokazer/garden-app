from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel
from app.domain.models.question import question_to_tag

class Tag(BaseModel, TimestampedModel):
    """Модель тега для вопросов"""
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Отношения
    questions: Mapped[List["Question"]] = relationship(
        "Question", secondary=question_to_tag, back_populates="tags"
    ) 