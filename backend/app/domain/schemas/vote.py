from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from app.domain.schemas.base import BaseSchema


class VoteTypeEnum(str, Enum):
    """Типы голосования за вопросы и ответы"""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"


class VoteBase(BaseSchema):
    """Базовая схема для голосования"""
    vote_type: VoteTypeEnum = Field(..., description="Тип голоса (за/против)")


class QuestionVoteCreate(VoteBase):
    """Схема для создания голоса за вопрос"""
    question_id: int = Field(..., description="ID вопроса, за который голосуют")


class AnswerVoteCreate(VoteBase):
    """Схема для создания голоса за ответ"""
    answer_id: int = Field(..., description="ID ответа, за который голосуют")


class VoteResponse(VoteBase, BaseSchema):
    """Схема ответа для голосования"""
    id: int = Field(..., description="Уникальный идентификатор голоса")
    user_id: int = Field(..., description="ID пользователя, который голосовал") 