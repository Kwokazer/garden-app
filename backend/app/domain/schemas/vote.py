# backend/app/domain/schemas/vote.py
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from app.domain.schemas.base import BaseSchema


class VoteTypeEnum(str, Enum):
    """Типы голосования за вопросы и ответы"""
    UP = "up"      # Изменено с UPVOTE
    DOWN = "down"  # Изменено с DOWNVOTE


class VoteBase(BaseSchema):
    """Базовая схема для голосования"""
    vote_type: VoteTypeEnum = Field(..., description="Тип голоса (за/против)")


class QuestionVoteCreate(VoteBase):
    """Схема для создания голоса за вопрос"""
    pass  # question_id передается в URL


class AnswerVoteCreate(VoteBase):
    """Схема для создания голоса за ответ"""
    pass  # answer_id передается в URL


class VoteResponse(VoteBase, BaseSchema):
    """Схема ответа для голосования"""
    id: int = Field(..., description="Уникальный идентификатор голоса")
    user_id: int = Field(..., description="ID пользователя, который голосовал")