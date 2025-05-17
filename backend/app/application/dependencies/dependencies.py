from typing import Annotated, Optional
from fastapi import Depends

from app.application.services.auth_service import AuthService
from app.application.services.user_service import UserService
from app.application.services.plant_service import PlantService
from app.domain.models.user import User
from app.infrastructure.database import get_db
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.cache.qa_cache import QACache

# Экземпляр Redis сервиса для использования во всем приложении
_redis_service = RedisService()

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

# ... [остальной код] 