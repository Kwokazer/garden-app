from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel
from app.domain.models.role import role_permission


class Permission(BaseModel):
    """Модель разрешений в системе"""
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Отношения
    roles: Mapped[List["Role"]] = relationship("Role", secondary=role_permission, back_populates="permissions")
    
    def __repr__(self) -> str:
        return f"<Permission {self.name}>" 