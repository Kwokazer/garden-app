import enum
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, validator

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema
from app.domain.schemas.utils import (validate_password_strength,
                                      validate_username)


class PrivacyLevelEnum(str, enum.Enum):
    """Enum для уровня приватности профиля"""
    PUBLIC = "public"
    LIMITED = "limited"
    PRIVATE = "private"

class RoleResponse(BaseSchema):
    """Схема для ответа с информацией о роли пользователя"""
    id: int
    name: str
    description: Optional[str] = None

class PermissionResponse(BaseSchema):
    """Схема для представления разрешения"""
    id: int
    name: str
    description: Optional[str] = None

class UserBase(BaseSchema):
    """Базовые поля пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    first_name: Optional[str] = Field(None, max_length=50, description="Имя")
    last_name: Optional[str] = Field(None, max_length=50, description="Фамилия")
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")
    bio: Optional[str] = Field(None, max_length=500, description="Биография/описание")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        error = validate_username(v)
        if error:
            raise ValueError(error)
        return v

class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class UserUpdate(BaseSchema):
    """Схема для обновления данных пользователя"""
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя пользователя")
    first_name: Optional[str] = Field(None, max_length=50, description="Имя")
    last_name: Optional[str] = Field(None, max_length=50, description="Фамилия")
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")
    bio: Optional[str] = Field(None, max_length=500, description="Биография/описание")
    privacy_level: Optional[PrivacyLevelEnum] = Field(None, description="Уровень приватности профиля")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if v is not None:
            error = validate_username(v)
            if error:
                raise ValueError(error)
        return v

class UserResponse(UserBase, IDSchema, TimestampedSchema):
    """Полная информация о пользователе для ответов API"""
    is_active: bool = Field(..., description="Статус активности пользователя")
    is_verified: bool = Field(..., description="Статус верификации email")
    privacy_level: PrivacyLevelEnum = Field(..., description="Уровень приватности профиля")
    roles: List[RoleResponse] = Field(default_factory=list, description="Роли пользователя в системе")

class UserDetailResponse(UserResponse):
    """Расширенная схема для представления данных пользователя"""
    permissions: List[PermissionResponse] = Field([], description="Разрешения пользователя")

class UserProfileResponse(BaseSchema):
    """Публичная информация о пользователе"""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime

class UserMeResponse(BaseSchema):
    """Схема для ответа /auth/me с упрощенными ролями"""
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    is_active: bool
    is_verified: bool
    privacy_level: PrivacyLevelEnum
    roles: List[str] = Field(default_factory=list, description="Названия ролей пользователя")

class UserListResponse(BaseSchema):
    """Схема для списка пользователей с пагинацией"""
    total: int
    page: int
    size: int
    items: List[UserResponse]

class UserRoleUpdate(BaseSchema):
    """Схема для обновления ролей пользователя"""
    user_id: int
    role_ids: List[int]

class ChangeRoleRequest(BaseSchema):
    """Запрос на изменение роли пользователя"""
    role_id: int

class AddRoleResponse(BaseSchema):
    """Ответ на добавление роли пользователю"""
    user_id: int
    role_id: int
    message: str

class RemoveRoleResponse(BaseSchema):
    """Ответ на удаление роли у пользователя"""
    user_id: int
    role_id: int
    message: str

class UserPublicResponse(BaseSchema):
    """Публичное представление пользователя с минимальной информацией"""
    id: int
    username: str
    avatar_url: Optional[str] = None
    created_at: datetime

class UserPasswordChange(BaseSchema):
    """Схема для изменения пароля пользователя"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль")
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class UserRef(BaseSchema):
    """Упрощенная схема пользователя для вложенного отображения"""
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., description="Имя пользователя")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    avatar_url: Optional[str] = Field(None, description="URL аватара")
