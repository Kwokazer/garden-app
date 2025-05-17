from typing import Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class TagBase(BaseSchema):
    """Базовые поля тега"""
    name: str = Field(..., description="Название тега", min_length=2, max_length=50)
    description: Optional[str] = Field(None, description="Описание тега", max_length=255)


class TagCreate(TagBase):
    """Схема для создания тега"""
    pass


class TagUpdate(BaseSchema):
    """Схема для обновления тега"""
    name: Optional[str] = Field(None, description="Название тега", min_length=2, max_length=50)
    description: Optional[str] = Field(None, description="Описание тега", max_length=255)


class TagResponse(TagBase, IDSchema, TimestampedSchema):
    """Схема ответа для тега"""
    pass


class TagRef(BaseSchema):
    """Упрощенная схема тега для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор тега")
    name: str = Field(..., description="Название тега") 