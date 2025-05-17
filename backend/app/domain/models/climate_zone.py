from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel

# Определение для использования во внешних импортах
plant_to_climate_zone = "plant_climate_zone"

class PlantToClimateZone(Base):
    """Модель связи растений и климатических зон (many-to-many)"""
    __tablename__ = "plant_climate_zone"
    
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), primary_key=True)
    climate_zone_id: Mapped[int] = mapped_column(ForeignKey("climate_zones.id"), primary_key=True)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_plant_climate_zone_plant", "plant_id"),
        Index("ix_plant_climate_zone_climate", "climate_zone_id"),
    )

class ClimateZone(BaseModel, TimestampedModel):
    """Модель климатической зоны"""
    __tablename__ = "climate_zones"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zone_number: Mapped[int] = mapped_column(nullable=False, unique=True, index=True)
    min_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Отношения
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", secondary=plant_to_climate_zone, back_populates="climate_zones"
    )
    
    def __repr__(self) -> str:
        return f"<ClimateZone {self.name} (Zone {self.zone_number})>" 