from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel

# Определение для использования во внешних импортах
question_to_tag = "question_tag"

class QuestionToTag(Base):
    """Модель связи между вопросами и тегами (many-to-many)"""
    __tablename__ = "question_tag"
    
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_question_tag_question", "question_id"),
        Index("ix_question_tag_tag", "tag_id"),
    )

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
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=question_to_tag, back_populates="questions"
    )
    plant: Mapped[Optional["Plant"]] = relationship("Plant", back_populates="questions") 