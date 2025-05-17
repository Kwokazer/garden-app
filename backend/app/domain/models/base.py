# backend/app/domain/models/base.py
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

class Base(DeclarativeBase):
    """База для всех SQLAlchemy моделей"""
    pass

class TimestampedModel:
    """Миксин для отслеживания времени создания и обновления"""
    __abstract__ = True
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

class BaseModel(Base):
    """Базовая модель для наследования другими моделями"""
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.id}>"