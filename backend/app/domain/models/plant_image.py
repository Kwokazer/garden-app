from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel, TimestampedModel

class PlantImage(BaseModel, TimestampedModel):
    """Модель изображения растения"""
    __tablename__ = "plant_images"
    
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Отношения
    plant: Mapped["Plant"] = relationship("Plant", back_populates="images")
    
    def __repr__(self) -> str:
        return f"<PlantImage {self.id} for plant_id={self.plant_id}>" 