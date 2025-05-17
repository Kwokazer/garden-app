# backend/app/domain/models/user.py
import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, BaseModel, TimestampedModel

# Перечисление для уровней приватности
class PrivacyLevel(enum.Enum):
    PUBLIC = "PUBLIC"       # Полный доступ к профилю для всех
    LIMITED = "LIMITED"     # Ограниченный доступ (основная информация)
    PRIVATE = "PRIVATE"     # Доступ только для авторизованных пользователей

# Определение для использования во внешних импортах
user_role = "user_role"

class UserRole(Base):
    """Модель связи пользователей и ролей (many-to-many)"""
    __tablename__ = "user_role"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("ix_user_role_user", "user_id"),
        Index("ix_user_role_role", "role_id"),
    )

class User(BaseModel, TimestampedModel):
    """Модель пользователя"""
    __tablename__ = "users"

    # Основная информация
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    
    # Статус и настройки
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    privacy_level: Mapped[PrivacyLevel] = mapped_column(Enum(PrivacyLevel), default=PrivacyLevel.LIMITED)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Верификация email
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Восстановление пароля
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    reset_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Отношения
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_role, back_populates="users"
    )
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="author", cascade="all, delete-orphan"
    )
    answers: Mapped[List["Answer"]] = relationship(
        "Answer", back_populates="author", cascade="all, delete-orphan"
    )
    
    # Вспомогательные методы
    def has_permission(self, permission_name: str) -> bool:
        """Проверить наличие разрешения у пользователя"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Проверить наличие роли у пользователя"""
        return any(role.name == role_name for role in self.roles)
    
    # Таблицы аргументов для индексов и других ограничений
    __table_args__ = (
        Index("ix_user_email_verification", "email", "is_verified"),
    )
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"