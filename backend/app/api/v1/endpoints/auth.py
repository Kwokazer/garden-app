import logging
from typing import Any, Dict

from fastapi import (APIRouter, BackgroundTasks, Body, Depends, HTTPException,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dependencies import get_auth_service, get_email_service
from app.application.dependencies.dependencies import get_current_active_user
from app.application.services.auth_service import AuthService
from app.domain.models.user import User
from app.domain.schemas.auth import (EmailVerificationRequest,
                                     EmailVerificationResponse, LoginRequest,
                                     PasswordResetConfirmRequest,
                                     PasswordResetConfirmResponse,
                                     PasswordResetRequest,
                                     PasswordResetResponse,
                                     RefreshTokenRequest, RegistrationRequest,
                                     RegistrationResponse, SuccessResponse,
                                     TokenResponse)
from app.domain.schemas.user import UserMeResponse
from app.infrastructure.external.email_service import EmailService

# Создаем роутер с зависимостью AuthService на уровне роутера
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Аутентификация пользователя по email и паролю
    """
    try:
        user = await auth_service.authenticate_user(login_data.email, login_data.password)
        tokens = await auth_service.create_tokens(user)
        return tokens
    except Exception as e:
        logger.error(f"Ошибка входа: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Обновление токенов с использованием refresh-токена
    """
    try:
        new_tokens = await auth_service.refresh_tokens(refresh_data.refresh_token)
        return new_tokens
    except Exception as e:
        logger.error(f"Ошибка обновления токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh-токен",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Выход пользователя из системы (инвалидация refresh-токена)
    """
    try:
        await auth_service.logout(refresh_data.refresh_token)
        return {"status": "success", "message": "Вы успешно вышли из системы"}
    except Exception as e:
        logger.error(f"Ошибка при выходе: {str(e)}")
        # Даже при ошибке возвращаем успех, т.к. клиенту не важно, был ли токен уже инвалидирован
        return {"status": "success", "message": "Вы успешно вышли из системы"}

@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(
    registration_data: RegistrationRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
) -> Dict[str, Any]:
    """
    Регистрация нового пользователя
    """
    try:
        user = await auth_service.register_user(registration_data.model_dump())
        
        # Добавляем отправку email с подтверждением в фоновой задаче
        if user.verification_token:
            background_tasks.add_task(
                email_service.send_verification_email, 
                user.email, 
                user.verification_token
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_verified": user.is_verified,
            "message": "Пользователь успешно зарегистрирован. Проверьте почту для подтверждения email."
        }
    except ValueError as e:
        logger.error(f"Ошибка валидации при регистрации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Подтверждение email пользователя
    """
    is_verified = await auth_service.verify_email(verification_data.verification_token)
    
    if is_verified:
        return {
            "is_verified": True,
            "message": "Email успешно подтвержден"
        }
    else:
        return {
            "is_verified": False,
            "message": "Неверный или устаревший токен подтверждения"
        }

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
) -> Dict[str, Any]:
    """
    Запрос на сброс пароля
    """
    reset_token = await auth_service.request_password_reset(reset_data.email)
    
    # В любом случае возвращаем успех для предотвращения перечисления пользователей
    if reset_token:
        # Добавляем отправку email с инструкциями в фоновой задаче
        background_tasks.add_task(
            email_service.send_password_reset_email, 
            reset_data.email, 
            reset_token
        )
    
    return {
        "message": "Инструкции по сбросу пароля отправлены на ваш email"
    }

@router.post("/reset-password-confirm", response_model=PasswordResetConfirmResponse)
async def reset_password_confirm(
    confirm_data: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Подтверждение сброса пароля
    """
    success = await auth_service.reset_password(confirm_data.reset_token, confirm_data.new_password)
    
    if success:
        return {
            "message": "Пароль успешно изменен"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или устаревший токен сброса пароля"
        )

@router.get("/me", response_model=UserMeResponse)
async def get_current_user(
    user: User = Depends(get_current_active_user)
) -> UserMeResponse:
    """
    Получение информации о текущем пользователе
    """
    return UserMeResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar_url=user.avatar_url,
        bio=None,  # Поле bio отсутствует в модели User
        created_at=user.created_at,
        is_active=user.is_active,
        is_verified=user.is_verified,
        privacy_level=user.privacy_level.value.lower(),
        roles=[role.name for role in user.roles] if user.roles else []
    )

@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    auth_service: AuthService = Depends(get_auth_service),
    user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Изменение пароля пользователя
    """
    try:
        await auth_service.change_password(
            user.id, 
            current_password, 
            new_password
        )
        return {
            "status": "success",
            "message": "Пароль успешно изменен"
        }
    except ValueError as e:
        logger.error(f"Ошибка валидации при смене пароля: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка при смене пароля: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при смене пароля"
        )