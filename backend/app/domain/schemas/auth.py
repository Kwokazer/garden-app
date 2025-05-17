import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from app.domain.schemas.base import BaseSchema
from app.domain.schemas.utils import (validate_password_strength,
                                      validate_username)


class Login(BaseSchema):
    """Схема для входа в систему"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")

class TokenResponse(BaseSchema):
    """Ответ с токенами доступа"""
    access_token: str = Field(..., description="JWT токен доступа")
    refresh_token: str = Field(..., description="Токен для обновления access токена")
    token_type: str = Field("bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

class TokenData(BaseSchema):
    """Данные, хранящиеся в JWT токене"""
    sub: str = Field(..., description="ID пользователя")
    exp: Optional[int] = None
    roles: Optional[list[str]] = Field(default_factory=list, description="Роли пользователя")

class PasswordReset(BaseSchema):
    """Схема для запроса сброса пароля"""
    email: EmailStr = Field(..., description="Email пользователя")

class PasswordResetConfirm(BaseSchema):
    """Схема для подтверждения сброса пароля"""
    token: str = Field(..., description="Токен для сброса пароля")
    password: str = Field(..., min_length=8, description="Новый пароль")
    
    @validator('password')
    @classmethod
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class EmailVerification(BaseSchema):
    """Схема для запроса верификации email"""
    token: str = Field(..., description="Токен для верификации email")

class OAuthLoginRequest(BaseSchema):
    """Схема для запроса OAuth авторизации"""
    provider: str = Field(..., description="Провайдер OAuth (google, vk, yandex)")
    code: str = Field(..., description="Авторизационный код от провайдера")
    redirect_uri: Optional[str] = Field(None, description="URI перенаправления после авторизации")
    
    @validator('provider')
    @classmethod
    def validate_provider(cls, v):
        allowed_providers = ["google", "vk", "yandex"]
        if v not in allowed_providers:
            raise ValueError(f"Провайдер {v} не поддерживается. Поддерживаемые провайдеры: {', '.join(allowed_providers)}")
        return v

class TokenRefresh(BaseSchema):
    """Схема для обновления токена"""
    refresh_token: str = Field(..., description="Токен для обновления")

class LoginRequest(BaseModel):
    """Запрос на аутентификацию"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")

class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str = Field(..., description="Refresh токен для обновления")

class RegistrationRequest(BaseModel):
    """Запрос на регистрацию нового пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")
    first_name: Optional[str] = Field(None, max_length=50, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=50, description="Фамилия пользователя")

    @validator('username')
    def username_alphanumeric(cls, v):
        error = validate_username(v)
        if error:
            raise ValueError(error)
        return v

    @validator('password')
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr = Field(..., description="Email пользователя")

class PasswordResetConfirmRequest(BaseModel):
    """Подтверждение сброса пароля"""
    reset_token: str = Field(..., description="Токен для сброса пароля")
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль")

    @validator('new_password')
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class ChangePasswordRequest(BaseModel):
    """Запрос на изменение пароля"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=8, max_length=100, description="Новый пароль")

    @validator('new_password')
    def password_strength(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

class EmailVerificationRequest(BaseModel):
    """Запрос на подтверждение email"""
    verification_token: str = Field(..., description="Токен для подтверждения email")

class OAuthCallbackRequest(BaseModel):
    """Данные обратного вызова от OAuth провайдера"""
    code: str = Field(..., description="Код авторизации от OAuth провайдера")
    state: Optional[str] = Field(None, description="Состояние для предотвращения CSRF")

class OAuthUserInfo(BaseModel):
    """Информация о пользователе, полученная от OAuth провайдера"""
    provider: str = Field(..., description="Название OAuth провайдера")
    provider_user_id: str = Field(..., description="ID пользователя у провайдера")
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Имя пользователя")
    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")
    access_token: str = Field(..., description="Access токен от провайдера")
    refresh_token: Optional[str] = Field(None, description="Refresh токен от провайдера")
    expires_at: Optional[datetime] = Field(None, description="Время истечения токена")
    token_type: Optional[str] = Field(None, description="Тип токена")
    scopes: Optional[List[str]] = Field(None, description="Предоставленные разрешения")

class RegistrationResponse(BaseModel):
    """Ответ на успешную регистрацию"""
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., description="Имя пользователя")
    is_verified: bool = Field(..., description="Флаг верификации email")
    message: str = Field("Пользователь успешно зарегистрирован", description="Сообщение об успешной регистрации")

class PasswordResetResponse(BaseModel):
    """Ответ на запрос сброса пароля"""
    message: str = Field("Инструкции по сбросу пароля отправлены на ваш email", 
                         description="Сообщение о результате запроса")

class PasswordResetConfirmResponse(BaseModel):
    """Ответ на подтверждение сброса пароля"""
    message: str = Field("Пароль успешно изменен", description="Сообщение о результате запроса")

class EmailVerificationResponse(BaseModel):
    """Ответ на подтверждение email"""
    is_verified: bool = Field(..., description="Результат верификации")
    message: str = Field(..., description="Сообщение о результате верификации")

class SuccessResponse(BaseModel):
    """Стандартный ответ об успешной операции"""
    status: str = Field("success", description="Статус операции")
    message: str = Field(..., description="Сообщение об успешной операции")
    data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")

class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""
    status: str = Field("error", description="Статус операции")
    message: str = Field(..., description="Сообщение об ошибке")
    error_code: Optional[str] = Field(None, description="Код ошибки")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали ошибки") 