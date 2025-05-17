from typing import Annotated, Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# Импортируем get_auth_service
from .services import get_auth_service 
from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.application.services.plant_service import PlantService
from app.domain.models.user import User
from app.infrastructure.database import get_db
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.cache.qa_cache import QACache

# Экземпляр Redis сервиса для использования во всем приложении
_redis_service = RedisService()

# Добавляем oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_redis_service() -> RedisService:
    """Предоставляет экземпляр RedisService"""
    await _redis_service.connect()
    return _redis_service

# Экземпляр QACache сервиса
_qa_cache = QACache(_redis_service)

async def get_qa_cache() -> QACache:
    """Предоставляет экземпляр QACache"""
    await _redis_service.connect()  # Убеждаемся, что Redis подключен
    return _qa_cache

# Новая функция для получения текущего активного пользователя
async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Получает текущего аутентифицированного и активного пользователя.
    """
    user = await auth_service.get_current_user(token=token)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return user

# ... [остальной код] 