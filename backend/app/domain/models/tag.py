from typing import List, Optional

from sqlalchemy import ForeignKey, String, Text, Index, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel


# Таблица связи растений и тегов (many-to-many)
plant_tag = Table(
    'plant_tag',
    Base.metadata,
    Column('plant_id', ForeignKey('plants.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True),
    # Индексы для оптимизации запросов
    Index('ix_plant_tag_plant', 'plant_id'),
    Index('ix_plant_tag_tag', 'tag_id'),
)


class Tag(BaseModel, TimestampedModel):
    """Модель тега"""
    __tablename__ = "tags"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Отношения
    plants: Mapped[List["Plant"]] = relationship(
        "Plant", secondary=plant_tag, back_populates="tags"
    )
    
    def __repr__(self) -> str:
        return f"<Tag {self.name}>"