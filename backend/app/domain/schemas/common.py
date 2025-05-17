from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from app.domain.schemas.base import BaseSchema

# Типовая переменная для использования в дженериках
T = TypeVar('T')


class PaginatedResponse(BaseSchema, Generic[T]):
    """Схема для пагинированных ответов API"""
    items: List[T] = Field(..., description="Список элементов")
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")


class SuccessResponse(BaseSchema):
    """Стандартный ответ об успешной операции"""
    status: str = Field("success", description="Статус операции")
    message: str = Field(..., description="Сообщение об успешной операции")
    data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class ErrorResponse(BaseSchema):
    """Стандартный ответ с ошибкой"""
    status: str = Field("error", description="Статус операции")
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(None, description="Код ошибки")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали ошибки") 