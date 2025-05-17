from typing import List, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel
from app.domain.models.user import user_role

# Определение для использования во внешних импортах
role_permission = "role_permission"

class RolePermission(Base):
    """Модель связи ролей и разрешений (many-to-many)"""
    __tablename__ = "role_permission"
    
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), primary_key=True)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_role_permission_role", "role_id"),
        Index("ix_role_permission_permission", "permission_id"),
    )

class Role(BaseModel, TimestampedModel):
    """Модель ролей пользователей в системе"""
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    
    # Отношения
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_role, back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permission, back_populates="roles",
        cascade="all, delete"
    )
    
    # Вспомогательный метод
    def has_permission(self, permission_name: str) -> bool:
        """Проверить наличие разрешения в роли"""
        return any(permission.name == permission_name for permission in self.permissions)