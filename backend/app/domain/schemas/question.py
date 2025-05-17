from typing import List, Optional, Dict, Any

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema
from app.domain.schemas.tag import TagRef


class QuestionBase(BaseSchema):
    """Базовые поля вопроса"""
    title: str = Field(..., description="Заголовок вопроса", min_length=5, max_length=255)
    body: str = Field(..., description="Содержание вопроса", min_length=10)
    plant_id: Optional[int] = Field(None, description="ID растения, связанного с вопросом")


class QuestionCreate(QuestionBase):
    """Схема для создания вопроса"""
    tags: Optional[List[str]] = Field(default_factory=list, description="Список названий тегов")


class QuestionUpdate(BaseSchema):
    """Схема для обновления вопроса"""
    title: Optional[str] = Field(None, description="Заголовок вопроса", min_length=5, max_length=255)
    body: Optional[str] = Field(None, description="Содержание вопроса", min_length=10)
    is_solved: Optional[bool] = Field(None, description="Отметка о решении вопроса")
    plant_id: Optional[int] = Field(None, description="ID растения, связанного с вопросом")
    tags: Optional[List[str]] = Field(None, description="Список названий тегов")


class QuestionResponse(QuestionBase, IDSchema, TimestampedSchema):
    """Базовая схема ответа для вопроса"""
    author_id: int = Field(..., description="ID автора вопроса")
    is_solved: bool = Field(..., description="Отметка о решении вопроса")
    view_count: int = Field(..., description="Количество просмотров")
    votes_up: int = Field(..., description="Количество голосов за")
    votes_down: int = Field(..., description="Количество голосов против")
    tags: List[TagRef] = Field(default_factory=list, description="Список тегов")


class QuestionDetailResponse(QuestionResponse):
    """Детальная схема ответа для вопроса с дополнительной информацией"""
    author: Dict[str, Any] = Field(..., description="Информация об авторе")
    answers_count: int = Field(0, description="Количество ответов")
    plant: Optional[Dict[str, Any]] = Field(None, description="Информация о связанном растении")
    answers: List[Dict[str, Any]] = Field(default_factory=list, description="Список ответов")
    user_vote: Optional[str] = Field(None, description="Тип голоса текущего пользователя")


class QuestionListResponse(BaseSchema):
    """Схема для списка вопросов с пагинацией"""
    items: List[QuestionResponse]
    total: int
    page: int
    size: int
    pages: int 