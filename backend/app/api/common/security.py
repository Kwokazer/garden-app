from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.domain.models.user import User

# Настройка OAuth2 для получения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Получить текущего пользователя из JWT токена
    
    Args:
        token: JWT токен из заголовка Authorization
        auth_service: Сервис аутентификации
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    try:
        user = await auth_service.get_current_user(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учетные данные",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Получить текущего активного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Текущий активный пользователь
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Получить текущего верифицированного пользователя
    
    Args:
        current_user: Текущий активный пользователь
        
    Returns:
        User: Текущий верифицированный пользователь
        
    Raises:
        HTTPException: Если email пользователя не подтвержден
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email пользователя не подтвержден"
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Получить текущего суперпользователя (с ролью admin)
    
    Args:
        current_user: Текущий активный пользователь
        
    Returns:
        User: Текущий суперпользователь
        
    Raises:
        HTTPException: Если у пользователя нет роли admin
    """
    if not current_user.has_role("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user

def check_permission(permission: str):
    """
    Проверить наличие определенного разрешения у пользователя
    
    Args:
        permission: Название разрешения
        
    Returns:
        Callable: Зависимость для проверки разрешения
    """
    async def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Отсутствует разрешение: {permission}"
            )
        return current_user
    
    return permission_dependency