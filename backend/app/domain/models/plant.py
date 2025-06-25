import enum
from typing import List, Optional

from sqlalchemy import Boolean, Enum, Float, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel
from app.domain.models.climate_zone import plant_to_climate_zone
from app.domain.models.plant_category import PlantCategory, plant_to_category   
from app.domain.models.plant_image import PlantImage


# Перечисление типов растений
class PlantType(str, enum.Enum):
    TREE = "TREE"              # Дерево
    SHRUB = "SHRUB"            # Кустарник
    FLOWER = "FLOWER"          # Цветок
    VEGETABLE = "VEGETABLE"    # Овощ
    FRUIT = "FRUIT"            # Фрукт
    HERB = "HERB"              # Трава/зелень
    SUCCULENT = "SUCCULENT"    # Суккулент
    VINE = "VINE"              # Лиана/вьющееся
    AQUATIC = "AQUATIC"        # Водное растение
    FERN = "FERN"              # Папоротник


# Перечисление жизненных циклов
class LifeCycle(str, enum.Enum):
    ANNUAL = "ANNUAL"          # Однолетнее
    BIENNIAL = "BIENNIAL"      # Двулетнее
    PERENNIAL = "PERENNIAL"    # Многолетнее


# Перечисление частоты полива
class WateringFrequency(str, enum.Enum):
    DAILY = "DAILY"
    TWICE_A_WEEK = "TWICE_A_WEEK"
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    RARELY = "RARELY"


# Перечисление уровней освещения
class LightLevel(str, enum.Enum):
    FULL_SUN = "FULL_SUN"
    PARTIAL_SUN = "PARTIAL_SUN"
    SHADE = "SHADE"
    LOW_LIGHT = "LOW_LIGHT"


# Перечисление уровней влажности
class HumidityLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# Перечисление сложности ухода
class CareDifficulty(str, enum.Enum):
    VERY_EASY = "VERY_EASY"
    EASY = "EASY"
    MODERATE = "MODERATE"
    DIFFICULT = "DIFFICULT"
    EXPERT = "EXPERT"


# Перечисление частоты подкормки
class FertilizingFrequency(str, enum.Enum):
    WEEKLY = "WEEKLY"
    BI_WEEKLY = "BI_WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"
    NONE = "NONE"


# Перечисление частоты пересадки
class RepottingFrequency(str, enum.Enum):
    ANNUALLY = "ANNUALLY"
    BI_ANNUALLY = "BI_ANNUALLY"
    THREE_YEARS = "THREE_YEARS"
    RARELY = "RARELY"


# Перечисление скорости роста
class GrowthRate(str, enum.Enum):
    FAST = "FAST"
    MODERATE = "MODERATE"
    SLOW = "SLOW"


class Plant(BaseModel, TimestampedModel):
    """Модель растения"""
    __tablename__ = "plants"

    # Основная информация
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latin_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)  # было scientific_name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Характеристики роста
    height_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # было growth_height_min
    height_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # было growth_height_max
    growth_rate: Mapped[Optional[GrowthRate]] = mapped_column(Enum(GrowthRate), nullable=True)
    
    # Тип растения и жизненный цикл
    plant_type: Mapped[Optional[PlantType]] = mapped_column(Enum(PlantType), nullable=True, index=True)
    life_cycle: Mapped[Optional[LifeCycle]] = mapped_column(Enum(LifeCycle), nullable=True)
    
    # Популярность
    popularity_score: Mapped[int] = mapped_column(default=0, index=True)
    
    # Цветение
    flowering_period: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # было bloom_season
    bloom_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Зоны морозостойкости
    hardiness_zone_min: Mapped[Optional[int]] = mapped_column(nullable=True)
    hardiness_zone_max: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Условия выращивания
    watering_frequency: Mapped[Optional[WateringFrequency]] = mapped_column(Enum(WateringFrequency), nullable=True)
    light_level: Mapped[Optional[LightLevel]] = mapped_column(Enum(LightLevel), nullable=True)
    temperature_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperature_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity_level: Mapped[Optional[HumidityLevel]] = mapped_column(Enum(HumidityLevel), nullable=True)
    
    # Уход
    care_difficulty: Mapped[Optional[CareDifficulty]] = mapped_column(Enum(CareDifficulty), nullable=True)
    fertilizing_frequency: Mapped[Optional[FertilizingFrequency]] = mapped_column(Enum(FertilizingFrequency), nullable=True)
    repotting_frequency: Mapped[Optional[RepottingFrequency]] = mapped_column(Enum(RepottingFrequency), nullable=True)
    
    # Безопасность
    is_toxic: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Инструкции и советы (подробные текстовые поля)
    care_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    planting_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # было planting_tips
    pruning_tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # JSON поля для сложных структур (будут обработаны в сервисном слое)
    care_tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON массив строк
    common_problems: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON массив объектов
    propagation_methods: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON массив объектов
    
    # Отношения
    categories: Mapped[List["PlantCategory"]] = relationship(
        "PlantCategory", secondary=plant_to_category, back_populates="plants"
    )
    climate_zones: Mapped[List["ClimateZone"]] = relationship(
        "ClimateZone", secondary=plant_to_climate_zone, back_populates="plants"
    )
    images: Mapped[List["PlantImage"]] = relationship(
        "PlantImage", back_populates="plant", cascade="all, delete-orphan",
        order_by="desc(PlantImage.is_primary), PlantImage.id"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary="plant_tag", back_populates="plants"
    )
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="plant")
    
    # Индексы
    __table_args__ = (
        Index('idx_plant_type_popularity', 'plant_type', 'popularity_score'),
        Index('idx_plant_care_difficulty', 'care_difficulty'),
        Index('idx_plant_watering_light', 'watering_frequency', 'light_level'),
    )