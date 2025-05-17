import logging

from app.infrastructure.cache.redis_service import RedisService, get_redis_service as get_redis
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Получение сервиса Redis из фабричной функции
async def get_redis_service() -> RedisService:
    """
    Зависимость для получения Redis-сервиса
    
    Returns:
        RedisService: Инстанс Redis-сервиса
    """
    try:
        return await get_redis()
    except Exception as e:
        logger.error(f"Ошибка при получении Redis-сервиса: {str(e)}")
        raise 