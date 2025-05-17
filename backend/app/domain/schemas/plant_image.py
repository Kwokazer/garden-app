from typing import Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class PlantImageBase(BaseSchema):
    """Базовые поля изображения растения"""
    image_url: str = Field(..., description="URL изображения растения")
    alt_text: Optional[str] = Field(None, description="Альтернативный текст для изображения")
    is_primary: bool = Field(False, description="Является ли изображение основным")


class PlantImageCreate(PlantImageBase):
    """Схема для создания изображения растения"""
    plant_id: int = Field(..., description="ID растения, к которому относится изображение")


class PlantImageUpdate(BaseSchema):
    """Схема для обновления изображения растения"""
    image_url: Optional[str] = Field(None, description="URL изображения растения")
    alt_text: Optional[str] = Field(None, description="Альтернативный текст для изображения")
    is_primary: Optional[bool] = Field(None, description="Является ли изображение основным")


class PlantImageResponse(PlantImageBase, IDSchema, TimestampedSchema):
    """Схема ответа для изображения растения"""
    plant_id: int = Field(..., description="ID растения, к которому относится изображение")


class PlantImageRef(BaseSchema):
    """Упрощенная схема изображения для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор изображения")
    image_url: str = Field(..., description="URL изображения растения")
    is_primary: bool = Field(..., description="Является ли изображение основным") 