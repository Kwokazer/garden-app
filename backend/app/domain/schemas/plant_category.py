from typing import Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class PlantCategoryBase(BaseSchema):
    """Базовые поля категории растений"""
    name: str = Field(..., description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории")


class PlantCategoryCreate(PlantCategoryBase):
    """Схема для создания категории растений"""
    pass


class PlantCategoryUpdate(BaseSchema):
    """Схема для обновления категории растений"""
    name: Optional[str] = Field(None, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    parent_id: Optional[int] = Field(None, description="ID родительской категории")


class PlantCategoryResponse(PlantCategoryBase, IDSchema, TimestampedSchema):
    """Схема ответа для категории растений"""
    pass


class PlantCategoryRef(BaseSchema):
    """Упрощенная схема категории для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории") 