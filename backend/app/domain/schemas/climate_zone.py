from typing import Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema


class ClimateZoneBase(BaseSchema):
    """Базовые поля климатической зоны"""
    name: str = Field(..., description="Название климатической зоны")
    description: Optional[str] = Field(None, description="Описание климатической зоны")
    zone_number: int = Field(..., description="Номер климатической зоны")
    min_temperature: Optional[float] = Field(None, description="Минимальная температура в Цельсиях")
    max_temperature: Optional[float] = Field(None, description="Максимальная температура в Цельсиях")


class ClimateZoneCreate(ClimateZoneBase):
    """Схема для создания климатической зоны"""
    pass


class ClimateZoneUpdate(BaseSchema):
    """Схема для обновления климатической зоны"""
    name: Optional[str] = Field(None, description="Название климатической зоны")
    description: Optional[str] = Field(None, description="Описание климатической зоны")
    zone_number: Optional[int] = Field(None, description="Номер климатической зоны")
    min_temperature: Optional[float] = Field(None, description="Минимальная температура в Цельсиях")
    max_temperature: Optional[float] = Field(None, description="Максимальная температура в Цельсиях")


class ClimateZoneResponse(ClimateZoneBase, IDSchema, TimestampedSchema):
    """Схема ответа для климатической зоны"""
    pass


class ClimateZoneRef(BaseSchema):
    """Упрощенная схема климатической зоны для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор климатической зоны")
    name: str = Field(..., description="Название климатической зоны")
    zone_number: int = Field(..., description="Номер климатической зоны") 