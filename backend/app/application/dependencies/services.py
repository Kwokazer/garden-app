from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.application.services.plant_service import PlantService
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.cache.plant_cache import PlantCacheService
from app.infrastructure.database import get_db

from .redis import get_redis_service


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
) -> AuthService:
    """
    Фабричная функция для получения сервиса аутентификации
    
    Args:
        db: Сессия базы данных
        redis_service: Redis-сервис
        
    Returns:
        AuthService: Инстанс сервиса аутентификации
    """
    # Создаем новый инстанс каждый раз, чтобы избежать проблем с асинхронным контекстом
    return AuthService(db=db, redis_cache=redis_service)

async def get_user_service(
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
) -> UserService:
    """
    Фабричная функция для получения сервиса пользователей
    
    Args:
        db: Сессия базы данных
        redis_service: Redis-сервис
        
    Returns:
        UserService: Инстанс сервиса пользователей
    """
    # Создаем новый инстанс каждый раз, чтобы избежать проблем с асинхронным контекстом
    return UserService(db=db, redis_service=redis_service)

async def get_plant_service(
    db: AsyncSession = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
) -> PlantService:
    """
    Фабричная функция для получения сервиса растений

    Args:
        db: Сессия базы данных
        redis_service: Redis-сервис

    Returns:
        PlantService: Инстанс сервиса растений
    """
    # Создаем кэш растений
    plant_cache = PlantCacheService(redis_service)
    # Создаем новый инстанс каждый раз, чтобы избежать проблем с асинхронным контекстом
    return PlantService(db, plant_cache)