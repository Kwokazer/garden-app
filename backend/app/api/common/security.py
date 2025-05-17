from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.domain.models.user import User

# Настройка OAuth2 для получения токена из заголовка Authorization
# Добавляем auto_error=False, чтобы схема не вызывала ошибку, если токен отсутствует
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scheme_name="JWT",
    auto_error=False 
)

async def get_current_user(
    # token: str = Depends(oauth2_scheme), # Теперь oauth2_scheme может вернуть None, поэтому тип token должен быть Optional[str]
    token: Optional[str] = Depends(oauth2_scheme), # oauth2_scheme теперь с auto_error=False
    auth_service: AuthService = Depends(get_auth_service)
) -> User: # Эта функция все еще должна возвращать User или вызывать ошибку, если токен есть, но он невалидный
    """
    Получить текущего пользователя из JWT токена.
    Вызывает ошибку, если токен предоставлен, но недействителен.
    """
    if not token: # Если токен не предоставлен (из-за auto_error=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user = await auth_service.get_current_user(token)
        return user
    except Exception as e: # Ловим ошибки от auth_service.get_current_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учетные данные", # Можно детализировать ошибку от auth_service, если нужно
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

def check_role(role_name: str):
    """
    Проверить наличие определенной роли у пользователя.

    Args:
        role_name: Название роли.

    Returns:
        Callable: Зависимость для проверки роли.
    """
    async def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not hasattr(current_user, 'has_role') or not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль: {role_name}"
            )
        return current_user
    return role_dependency

async def optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme), # oauth2_scheme теперь с auto_error=False
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Получить текущего пользователя, если токен предоставлен и валиден.
    Возвращает None, если пользователь не аутентифицирован или токен не предоставлен.
    """
    if not token: # Если токен не предоставлен (oauth2_scheme вернет None)
        return None
    try:
        # AuthService.get_current_user должен сам обрабатывать ошибки и может вызывать AuthenticationError
        user = await auth_service.get_current_user(token)
        # Дополнительно проверим активность пользователя, как в get_current_active_user, если это нужно для optional_current_user
        # if not user.is_active:
        #     return None # Или можно оставить как есть, если get_current_user уже это проверяет
        return user
    except Exception: # Ловим любые исключения от auth_service.get_current_user или _decode_token
        return None