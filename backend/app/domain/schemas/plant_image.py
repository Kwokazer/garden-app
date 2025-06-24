from typing import Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class PlantImageBase(BaseSchema):
    """Базовые поля изображения растения"""
    url: str = Field(..., description="URL изображения растения")
    alt: Optional[str] = Field(None, description="Альтернативный текст для изображения")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    description: Optional[str] = Field(None, description="Описание изображения")
    thumbnail_url: Optional[str] = Field(None, description="URL миниатюры")
    is_primary: bool = Field(False, description="Является ли изображение основным")


class PlantImageCreate(PlantImageBase):
    """Схема для создания изображения растения"""
    plant_id: int = Field(..., description="ID растения, к которому относится изображение")


class PlantImageUpdate(BaseSchema):
    """Схема для обновления изображения растения"""
    url: Optional[str] = Field(None, description="URL изображения растения")
    alt: Optional[str] = Field(None, description="Альтернативный текст для изображения")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    description: Optional[str] = Field(None, description="Описание изображения")
    thumbnail_url: Optional[str] = Field(None, description="URL миниатюры")
    is_primary: Optional[bool] = Field(None, description="Является ли изображение основным")


class PlantImageResponse(PlantImageBase, IDSchema, TimestampedSchema):
    """Схема ответа для изображения растения"""
    plant_id: int = Field(..., description="ID растения, к которому относится изображение")


class PlantImageRef(BaseSchema):
    """Упрощенная схема изображения для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор изображения")
    url: str = Field(..., description="URL изображения")
    alt: Optional[str] = Field(None, description="Альтернативный текст")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    is_primary: bool = Field(False, description="Основное изображение")