import enum
from typing import List, Optional

from sqlalchemy import Enum, Float, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel
from app.domain.models.climate_zone import plant_to_climate_zone
from app.domain.models.plant_category import PlantCategory, plant_to_category   
from app.domain.models.plant_image import PlantImage



# Перечисление типов растений
class PlantType(str, enum.Enum):
   TREE = "tree"              # Дерево
   SHRUB = "shrub"            # Кустарник
   FLOWER = "flower"          # Цветок
   VEGETABLE = "vegetable"    # Овощ
   FRUIT = "fruit"            # Фрукт
   HERB = "herb"              # Трава/зелень
   SUCCULENT = "succulent"    # Суккулент
   VINE = "vine"              # Лиана/вьющееся
   AQUATIC = "aquatic"        # Водное растение
   FERN = "fern"              # Папоротник

class Plant(BaseModel, TimestampedModel):
   """Модель растения"""
   __tablename__ = "plants"

   # Основная информация
   name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
   scientific_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
   description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
   # Характеристики роста
   growth_height_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
   growth_height_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
   growth_rate: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
   
   # Тип растения и популярность
   plant_type: Mapped[Optional[PlantType]] = mapped_column(Enum(PlantType), nullable=True, index=True)
   popularity_score: Mapped[int] = mapped_column(default=0, index=True)
   
   # Дополнительная информация
   bloom_season: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
   bloom_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
   hardiness_zone_min: Mapped[Optional[int]] = mapped_column(nullable=True)
   hardiness_zone_max: Mapped[Optional[int]] = mapped_column(nullable=True)
   
   # Рекомендации по уходу
   care_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   planting_tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   pruning_tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
   # Отношения
   categories: Mapped[List["PlantCategory"]] = relationship(
       "PlantCategory", secondary=plant_to_category, back_populates="plants"
   )
   climate_zones: Mapped[List["ClimateZone"]] = relationship(
       "ClimateZone", secondary=plant_to_climate_zone, back_populates="plants"
   )
   images: Mapped[List["PlantImage"]] = relationship(
       "PlantImage", back_populates="plant", cascade="all, delete-orphan"
   )
   questions: Mapped[List["Question"]] = relationship("Question", back_populates="plant")
   
   # Индексы
   __table_args__ = (
       Index('idx_plant_type_popularity', 'plant_type', 'popularity_score'),
   )