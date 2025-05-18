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
    TREE = "TREE"
    SHRUB = "SHRUB"
    FLOWER = "FLOWER"
    VEGETABLE = "VEGETABLE"
    FRUIT = "FRUIT"
    HERB = "HERB"
    SUCCULENT = "SUCCULENT"
    VINE = "VINE"
    AQUATIC = "AQUATIC"
    FERN = "FERN"

class LifeCycleEnum(str, enum.Enum):
    ANNUAL = "ANNUAL"
    BIENNIAL = "BIENNIAL"
    PERENNIAL = "PERENNIAL"

class WateringFrequencyEnum(str, enum.Enum):
    DAILY = "DAILY"
    TWICE_A_WEEK = "TWICE_A_WEEK"
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    RARELY = "RARELY"

class LightLevelEnum(str, enum.Enum):
    FULL_SUN = "FULL_SUN"
    PARTIAL_SUN = "PARTIAL_SUN"
    SHADE = "SHADE"
    LOW_LIGHT = "LOW_LIGHT"

class HumidityLevelEnum(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CareDifficultyEnum(str, enum.Enum):
    VERY_EASY = "VERY_EASY"
    EASY = "EASY"
    MODERATE = "MODERATE"
    DIFFICULT = "DIFFICULT"
    EXPERT = "EXPERT"

class FertilizingFrequencyEnum(str, enum.Enum):
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    NONE = "NONE"

class RepottingFrequencyEnum(str, enum.Enum):
    ANNUALLY = "ANNUALLY"
    BI_ANNUALLY = "BI_ANNUALLY"
    THREE_YEARS = "THREE_YEARS"
    RARELY = "RARELY"

# ВАЖНО: Если в БД enum создан с заглавными буквами, нужно исправить значения
class GrowthRateEnum(str, enum.Enum):
    # Если в PostgreSQL enum growthrate создан как ('FAST','MODERATE','SLOW')
    FAST = "FAST"         # Соответствует БД enum
    MODERATE = "MODERATE" # Соответствует БД enum  
    SLOW = "SLOW"   


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


class PlantListResponse(BaseSchema):
    """Схема ответа для списка растений с пагинацией"""
    items: List[PlantResponse] = Field(..., description="Список растений")
    total_items: int = Field(..., description="Общее количество элементов")  # Изменено с total
    total_pages: int = Field(..., description="Общее количество страниц")    # Изменено с pages
    page: int = Field(..., description="Текущая страница")
    per_page: int = Field(..., description="Количество элементов на странице")  # Изменено с size


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