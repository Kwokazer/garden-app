import enum
import json
from typing import List, Optional, Dict, Any

from pydantic import Field, field_validator

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema
from app.domain.schemas.climate_zone import ClimateZoneRef
from app.domain.schemas.plant_category import PlantCategoryRef
from app.domain.schemas.plant_image import PlantImageRef
from app.domain.schemas.tag import TagRef
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


class LifeCycleEnum(str, enum.Enum):
    """Жизненные циклы растений"""
    ANNUAL = "annual"
    BIENNIAL = "biennial"
    PERENNIAL = "perennial"


class WateringFrequencyEnum(str, enum.Enum):
    """Частота полива"""
    DAILY = "daily"
    TWICE_A_WEEK = "twice_a_week"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    RARELY = "rarely"


class LightLevelEnum(str, enum.Enum):
    """Уровни освещения"""
    FULL_SUN = "full_sun"
    PARTIAL_SUN = "partial_sun"
    SHADE = "shade"
    LOW_LIGHT = "low_light"


class HumidityLevelEnum(str, enum.Enum):
    """Уровни влажности"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CareDifficultyEnum(str, enum.Enum):
    """Сложность ухода"""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    EXPERT = "expert"


class FertilizingFrequencyEnum(str, enum.Enum):
    """Частота подкормки"""
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    NONE = "none"


class RepottingFrequencyEnum(str, enum.Enum):
    """Частота пересадки"""
    ANNUALLY = "annually"
    BI_ANNUALLY = "bi_annually"
    THREE_YEARS = "three_years"
    RARELY = "rarely"


class GrowthRateEnum(str, enum.Enum):
    """Скорость роста"""
    FAST = "fast"
    MODERATE = "moderate"
    SLOW = "slow"


class PlantBase(BaseSchema):
    """Базовые поля растения"""
    name: str = Field(..., description="Название растения")
    latin_name: Optional[str] = Field(None, description="Латинское название растения")
    description: Optional[str] = Field(None, description="Описание растения")
    
    # Характеристики роста
    height_min: Optional[float] = Field(None, description="Минимальная высота роста (см)")
    height_max: Optional[float] = Field(None, description="Максимальная высота роста (см)")
    growth_rate: Optional[GrowthRateEnum] = Field(None, description="Скорость роста")
    
    # Тип растения и жизненный цикл
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Тип растения")
    life_cycle: Optional[LifeCycleEnum] = Field(None, description="Жизненный цикл растения")
    popularity_score: Optional[int] = Field(0, description="Рейтинг популярности (чем выше, тем популярнее)")
    
    # Цветение
    flowering_period: Optional[str] = Field(None, description="Период цветения")
    bloom_color: Optional[str] = Field(None, description="Цвет цветов")
    hardiness_zone_min: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    hardiness_zone_max: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    
    # Условия выращивания
    watering_frequency: Optional[WateringFrequencyEnum] = Field(None, description="Частота полива")
    light_level: Optional[LightLevelEnum] = Field(None, description="Уровень освещения")
    temperature_min: Optional[float] = Field(None, description="Минимальная температура (°C)")
    temperature_max: Optional[float] = Field(None, description="Максимальная температура (°C)")
    humidity_level: Optional[HumidityLevelEnum] = Field(None, description="Уровень влажности")
    
    # Уход
    care_difficulty: Optional[CareDifficultyEnum] = Field(None, description="Сложность ухода")
    fertilizing_frequency: Optional[FertilizingFrequencyEnum] = Field(None, description="Частота подкормки")
    repotting_frequency: Optional[RepottingFrequencyEnum] = Field(None, description="Частота пересадки")
    
    # Безопасность
    is_toxic: Optional[bool] = Field(False, description="Токсично ли растение")
    
    # Инструкции и советы
    care_instructions: Optional[str] = Field(None, description="Инструкции по уходу")
    planting_instructions: Optional[str] = Field(None, description="Инструкции по посадке")
    pruning_tips: Optional[str] = Field(None, description="Советы по обрезке")
    notes: Optional[str] = Field(None, description="Дополнительные примечания")


class PlantCreate(PlantBase):
    """Схема для создания растения"""
    category_ids: Optional[List[int]] = Field(default_factory=list, description="ID категорий растения")
    climate_zone_ids: Optional[List[int]] = Field(default_factory=list, description="ID климатических зон")
    tag_ids: Optional[List[int]] = Field(default_factory=list, description="ID тегов")
    
    # Массивы для сложных структур
    care_tips: Optional[List[str]] = Field(default_factory=list, description="Советы по уходу")
    common_problems: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Частые проблемы")
    propagation_methods: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Методы размножения")


class PlantUpdate(BaseSchema):
    """Схема для обновления растения"""
    name: Optional[str] = Field(None, description="Название растения")
    latin_name: Optional[str] = Field(None, description="Латинское название растения")
    description: Optional[str] = Field(None, description="Описание растения")
    
    # Характеристики роста
    height_min: Optional[float] = Field(None, description="Минимальная высота роста (см)")
    height_max: Optional[float] = Field(None, description="Максимальная высота роста (см)")
    growth_rate: Optional[GrowthRateEnum] = Field(None, description="Скорость роста")
    
    # Тип растения и жизненный цикл
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Тип растения")
    life_cycle: Optional[LifeCycleEnum] = Field(None, description="Жизненный цикл растения")
    popularity_score: Optional[int] = Field(None, description="Рейтинг популярности")
    
    # Цветение
    flowering_period: Optional[str] = Field(None, description="Период цветения")
    bloom_color: Optional[str] = Field(None, description="Цвет цветов")
    hardiness_zone_min: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    hardiness_zone_max: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    
    # Условия выращивания
    watering_frequency: Optional[WateringFrequencyEnum] = Field(None, description="Частота полива")
    light_level: Optional[LightLevelEnum] = Field(None, description="Уровень освещения")
    temperature_min: Optional[float] = Field(None, description="Минимальная температура (°C)")
    temperature_max: Optional[float] = Field(None, description="Максимальная температура (°C)")
    humidity_level: Optional[HumidityLevelEnum] = Field(None, description="Уровень влажности")
    
    # Уход
    care_difficulty: Optional[CareDifficultyEnum] = Field(None, description="Сложность ухода")
    fertilizing_frequency: Optional[FertilizingFrequencyEnum] = Field(None, description="Частота подкормки")
    repotting_frequency: Optional[RepottingFrequencyEnum] = Field(None, description="Частота пересадки")
    
    # Безопасность
    is_toxic: Optional[bool] = Field(None, description="Токсично ли растение")
    
    # Инструкции и советы
    care_instructions: Optional[str] = Field(None, description="Инструкции по уходу")
    planting_instructions: Optional[str] = Field(None, description="Инструкции по посадке")
    pruning_tips: Optional[str] = Field(None, description="Советы по обрезке")
    notes: Optional[str] = Field(None, description="Дополнительные примечания")
    
    # Связи
    category_ids: Optional[List[int]] = Field(None, description="ID категорий растения")
    climate_zone_ids: Optional[List[int]] = Field(None, description="ID климатических зон")
    tag_ids: Optional[List[int]] = Field(None, description="ID тегов")
    
    # Массивы для сложных структур
    care_tips: Optional[List[str]] = Field(None, description="Советы по уходу")
    common_problems: Optional[List[Dict[str, Any]]] = Field(None, description="Частые проблемы")
    propagation_methods: Optional[List[Dict[str, Any]]] = Field(None, description="Методы размножения")


class PlantResponse(PlantBase, IDSchema, TimestampedSchema):
    """Схема ответа для растения"""
    # Связанные данные  
    category: Optional[PlantCategoryRef] = Field(None, description="Основная категория растения")
    categories: List[PlantCategoryRef] = Field(default_factory=list, description="Все категории растения")
    climate_zones: List[ClimateZoneRef] = Field(default_factory=list, description="Климатические зоны растения")
    images: List[PlantImageRef] = Field(default_factory=list, description="Изображения растения")
    tags: List[TagRef] = Field(default_factory=list, description="Теги растения")
    
    # Массивы для сложных структур (десериализованные из JSON)
    care_tips: List[str] = Field(default_factory=list, description="Советы по уходу")
    common_problems: List[Dict[str, Any]] = Field(default_factory=list, description="Частые проблемы")
    propagation_methods: List[Dict[str, Any]] = Field(default_factory=list, description="Методы размножения")
    
    @field_validator('care_tips', mode='before')
    @classmethod
    def parse_care_tips(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []
    
    @field_validator('common_problems', mode='before')
    @classmethod
    def parse_common_problems(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []
    
    @field_validator('propagation_methods', mode='before')
    @classmethod
    def parse_propagation_methods(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []
    
    @field_validator('category', mode='before')
    @classmethod
    def set_primary_category(cls, v, info):
        # Если category не задана, берем первую из categories
        if v is None and 'categories' in info.data:
            categories = info.data['categories']
            if categories:
                return categories[0]
        return v


class PlantListResponse(PaginatedResponse[PlantResponse]):
    """Пагинированный список растений"""
    pass


class PlantFilterParams(BaseSchema):
    """Параметры фильтрации растений"""
    name: Optional[str] = Field(None, description="Поиск по имени (частичное совпадение)")
    category_id: Optional[int] = Field(None, description="Фильтр по ID категории")
    climate_zone_id: Optional[int] = Field(None, description="Фильтр по ID климатической зоны")
    tag_id: Optional[int] = Field(None, description="Фильтр по ID тега")
    plant_type: Optional[PlantTypeEnum] = Field(None, description="Фильтр по типу растения")
    life_cycle: Optional[LifeCycleEnum] = Field(None, description="Фильтр по жизненному циклу")
    min_popularity: Optional[int] = Field(None, ge=0, description="Минимальный рейтинг популярности")
    min_hardiness_zone: Optional[int] = Field(None, description="Минимальная зона морозостойкости")
    max_hardiness_zone: Optional[int] = Field(None, description="Максимальная зона морозостойкости")
    watering_frequency: Optional[WateringFrequencyEnum] = Field(None, description="Частота полива")
    light_level: Optional[LightLevelEnum] = Field(None, description="Уровень освещения")
    care_difficulty: Optional[CareDifficultyEnum] = Field(None, description="Сложность ухода")
    is_toxic: Optional[bool] = Field(None, description="Токсичность растения")
    min_height: Optional[float] = Field(None, description="Минимальная высота растения (см)")
    max_height: Optional[float] = Field(None, description="Максимальная высота растения (см)")
    min_temperature: Optional[float] = Field(None, description="Минимальная температура (°C)")
    max_temperature: Optional[float] = Field(None, description="Максимальная температура (°C)")