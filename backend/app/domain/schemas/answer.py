from typing import Dict, Any, Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class AnswerBase(BaseSchema):
    """Базовые поля ответа"""
    body: str = Field(..., description="Содержание ответа", min_length=5)


class AnswerCreate(AnswerBase):
    """Схема для создания ответа"""
    question_id: int = Field(..., description="ID вопроса, на который дается ответ")


class AnswerUpdate(BaseSchema):
    """Схема для обновления ответа"""
    body: Optional[str] = Field(None, description="Содержание ответа", min_length=5)
    is_accepted: Optional[bool] = Field(None, description="Принят ли ответ как решение")


class AnswerResponse(AnswerBase, IDSchema, TimestampedSchema):
    """Базовая схема ответа для API"""
    author_id: int = Field(..., description="ID автора ответа")
    question_id: int = Field(..., description="ID вопроса")
    is_accepted: bool = Field(..., description="Принят ли ответ как решение")
    votes_up: int = Field(..., description="Количество голосов за")
    votes_down: int = Field(..., description="Количество голосов против")


class AnswerDetailResponse(AnswerResponse):
    """Детальная схема ответа с информацией об авторе"""
    author: Dict[str, Any] = Field(..., description="Информация об авторе")
    user_vote: Optional[str] = Field(None, description="Тип голоса текущего пользователя") 