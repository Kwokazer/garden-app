from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

# Перечисление для типов голосов
class VoteType(str, Enum):
    """Типы голосов для вопросов и ответов"""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"

class QuestionVote(BaseModel, TimestampedModel):
    """Модель голоса за вопрос"""
    __tablename__ = "question_votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    vote_type: Mapped[VoteType] = mapped_column(String(10), nullable=False)

    # Отношения
    user: Mapped["User"] = relationship("User")
    question: Mapped["Question"] = relationship("Question")

class AnswerVote(BaseModel, TimestampedModel):
    """Модель голоса за ответ"""
    __tablename__ = "answer_votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"), nullable=False)
    vote_type: Mapped[VoteType] = mapped_column(String(10), nullable=False)

    # Отношения
    user: Mapped["User"] = relationship("User")
    answer: Mapped["Answer"] = relationship("Answer") 