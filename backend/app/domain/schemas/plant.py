import enum
from typing import List, Optional

from pydantic import Field

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema
from app.domain.schemas.climate_zone import ClimateZoneRef
from app.domain.schemas.plant_category import PlantCategoryRef
from app.domain.schemas.plant_image import PlantImageRef
from app.domain.schemas.common import PaginatedResponse


class PlantTypeEnum(str, enum.Enum):
    """Типы растений"""
    TREE = "tree"
    SHRUB = "shrub"
    FLOWER = "flower"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    HERB = "herb"
    SUCCULENT = "succulent"
    VINE = "vine"
    AQUATIC = "aquatic"
    FERN = "fern"


class PlantBase(BaseSchema):
    """Базовые поля растения"""
    name: str = Field(..., description="Название растения")
    scientific_name: Optional[str] = Field(None, description="Научное название растения")
    description: Optional[str] = Field(None, description="Описание растения")
    
    # Характеристики роста
    growth_height_min: Optional[float] = Field(None, description="Минимальная высота роста (см)")
    growth_height_max: Optional[float] = Field(None, description="Максимальная высота роста (см)")
    growth_rate: Optional[str] = Field(None, description="Скорость роста")
    
    # Тип растения и популярность
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Тип растения")
    popularity_score: Optional[int] = Field(0, description="Рейтинг популярности (чем выше, тем популярнее)")
    
    # Дополнительная информация
    bloom_season: Optional[str] = Field(None, description="Сезон цветения")
    bloom_color: Optional[str] = Field(None, description="Цвет цветов")
    hardiness_zone_min: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    hardiness_zone_max: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    
    # Рекомендации по уходу
    care_instructions: Optional[str] = Field(None, description="Инструкции по уходу")
    planting_tips: Optional[str] = Field(None, description="Советы по посадке")
    pruning_tips: Optional[str] = Field(None, description="Советы по обрезке")


class PlantCreate(PlantBase):
    """Схема для создания растения"""
    category_ids: Optional[List[int]] = Field(default_factory=list, description="ID категорий растения")
    climate_zone_ids: Optional[List[int]] = Field(default_factory=list, description="ID климатических зон")


class PlantUpdate(BaseSchema):
    """Схема для обновления растения"""
    name: Optional[str] = Field(None, description="Название растения")
    scientific_name: Optional[str] = Field(None, description="Научное название растения")
    description: Optional[str] = Field(None, description="Описание растения")
    
    # Характеристики роста
    growth_height_min: Optional[float] = Field(None, description="Минимальная высота роста (см)")
    growth_height_max: Optional[float] = Field(None, description="Максимальная высота роста (см)")
    growth_rate: Optional[str] = Field(None, description="Скорость роста")
    
    # Тип растения и популярность
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Тип растения")
    popularity_score: Optional[int] = Field(None, description="Рейтинг популярности (чем выше, тем популярнее)")
    
    # Дополнительная информация
    bloom_season: Optional[str] = Field(None, description="Сезон цветения")
    bloom_color: Optional[str] = Field(None, description="Цвет цветов")
    hardiness_zone_min: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    hardiness_zone_max: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    
    # Рекомендации по уходу
    care_instructions: Optional[str] = Field(None, description="Инструкции по уходу")
    planting_tips: Optional[str] = Field(None, description="Советы по посадке")
    pruning_tips: Optional[str] = Field(None, description="Советы по обрезке")
    
    # Связи
    category_ids: Optional[List[int]] = Field(None, description="ID категорий растения")
    climate_zone_ids: Optional[List[int]] = Field(None, description="ID климатических зон")


class PlantResponse(PlantBase, IDSchema, TimestampedSchema):
    """Схема ответа для растения"""
    categories: List[PlantCategoryRef] = Field(default_factory=list, description="Категории растения")
    climate_zones: List[ClimateZoneRef] = Field(default_factory=list, description="Климатические зоны растения")
    images: List[PlantImageRef] = Field(default_factory=list, description="Изображения растения")


class PlantListResponse(PaginatedResponse[PlantResponse]):
    """Пагинированный список растений"""
    pass


class PlantFilterParams(BaseSchema):
    """Параметры фильтрации растений"""
    name: Optional[str] = Field(None, description="Поиск по имени (частичное совпадение)")
    category_id: Optional[int] = Field(None, description="Фильтр по ID категории")
    climate_zone_id: Optional[int] = Field(None, description="Фильтр по ID климатической зоны")
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Фильтр по типу растения")
    min_popularity: Optional[int] = Field(None, ge=0, description="Минимальный рейтинг популярности")
    min_hardiness_zone: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    max_hardiness_zone: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    min_climate_zone: Optional[int] = Field(None, description="Минимальная климатическая зона")
    max_climate_zone: Optional[int] = Field(None, description="Максимальная климатическая зона")
    growth_rate: Optional[str] = Field(None, description="Скорость роста")
    water_requirements: Optional[str] = Field(None, description="Требования к поливу")
    sun_requirements: Optional[str] = Field(None, description="Требования к освещению")
    min_height: Optional[float] = Field(None, description="Минимальная высота растения (см)")
    max_height: Optional[float] = Field(None, description="Максимальная высота растения (см)")

