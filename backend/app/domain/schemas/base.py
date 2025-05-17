from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Типовая переменная для использования в дженериках
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Базовая схема с настройками для всех моделей"""
    model_config = ConfigDict(
        from_attributes=True,  # Для поддержки взаимодействия с ORM
        populate_by_name=True,  # Для поддержки алиасов полей
        arbitrary_types_allowed=True  # Разрешить произвольные типы
    )

class TimestampedSchema(BaseSchema):
    """Схема с полями времени создания и обновления"""
    created_at: datetime = Field(None, description="Дата и время создания записи")
    updated_at: Optional[datetime] = Field(None, description="Дата и время последнего обновления записи")

class IDSchema(BaseSchema):
    """Схема с полем идентификатора"""
    id: int = Field(..., description="Уникальный идентификатор записи")

class PaginatedResponse(BaseSchema, Generic[T]):
    """Схема для пагинированных ответов API"""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
