from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text, Index, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel


class PlantToCategory(Base):
    """Модель связи растений и категорий (many-to-many)"""
    __tablename__ = "plant_category"
    
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("plant_categories.id"), primary_key=True)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_plant_category_plant", "plant_id"),
        Index("ix_plant_category_category", "category_id"),
    )

# Определение для использования во внешних импортах
# Получение объекта Table из модели для использования в join
plant_to_category = PlantToCategory.__table__

class PlantCategory(BaseModel, TimestampedModel):
    """Модель категории растений"""
    __tablename__ = "plant_categories"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("plant_categories.id"), nullable=True)
    
    # Отношения
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", secondary=plant_to_category, back_populates="categories"
    )
    subcategories: Mapped[List["PlantCategory"]] = relationship(
        "PlantCategory", 
        back_populates="parent",
        cascade="all, delete"
    )
    parent: Mapped[Optional["PlantCategory"]] = relationship(
        "PlantCategory", 
        back_populates="subcategories",
        remote_side="PlantCategory.id"
    )
    
    def __repr__(self) -> str:
        return f"<PlantCategory {self.name}>" 