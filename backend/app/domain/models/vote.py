# backend/app/domain/models/vote.py
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

# Перечисление для типов голосов
class VoteType(str, Enum):
    """Типы голосов для вопросов и ответов"""
    UP = "up"      # Изменено с UPVOTE
    DOWN = "down"  # Изменено с DOWNVOTE

class QuestionVote(BaseModel, TimestampedModel):
    """Модель голоса за вопрос"""
    __tablename__ = "question_votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    vote_type: Mapped[VoteType] = mapped_column(String(10), nullable=False)

    # Отношения
    user: Mapped["User"] = relationship("User")
    question: Mapped["Question"] = relationship("Question")
    
    # Уникальное ограничение - один пользователь может голосовать за вопрос только один раз
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_question_vote'),
    )

class AnswerVote(BaseModel, TimestampedModel):
    """Модель голоса за ответ"""
    __tablename__ = "answer_votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), nullable=False)
    vote_type: Mapped[VoteType] = mapped_column(String(10), nullable=False)

    # Отношения
    user: Mapped["User"] = relationship("User")
    answer: Mapped["Answer"] = relationship("Answer")
    
    # Уникальное ограничение - один пользователь может голосовать за ответ только один раз
    __table_args__ = (
        UniqueConstraint('user_id', 'answer_id', name='uq_user_answer_vote'),
    )