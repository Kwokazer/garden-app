import json
import logging
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Сервис для работы с Redis"""
    
    def __init__(self):
        try:
            # Формирование URL подключения к Redis
            if settings.REDIS_PASSWORD:
                redis_url = f"redis://{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            else:
                redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
                
            # Создание соединения с Redis
            self.redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Ошибка при инициализации Redis: {str(e)}")
            # Создаем заглушку при ошибке подключения
            self.redis = None
    
    async def close(self):
        """Закрыть соединение с Redis"""
        if self.redis:
            await self.redis.close()
    
    async def is_connected(self) -> bool:
        """Проверить соединение с Redis"""
        try:
            if self.redis:
                return await self.redis.ping()
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке соединения с Redis: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу"""
        try:
            if self.redis:
                return await self.redis.get(key)
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении значения из Redis: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, Dict, List], 
        expire: Optional[int] = None
    ) -> bool:
        """
        Установить значение по ключу
        
        Args:
            key: Ключ
            value: Значение (строка или объект для сериализации)
            expire: Время жизни в секундах
            
        Returns:
            bool: Успешность операции
        """
        try:
            if not self.redis:
                return False
                
            # Сериализуем значение, если это не строка
            if not isinstance(value, str):
                value = json.dumps(value)
                
            # Устанавливаем значение
            if expire:
                return await self.redis.setex(key, expire, value)
            else:
                return await self.redis.set(key, value)
        except Exception as e:
            logger.error(f"Ошибка при установке значения в Redis: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить значение по ключу"""
        try:
            if self.redis:
                return await self.redis.delete(key) > 0
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении значения из Redis: {str(e)}")
            return False
    
    async def add_token_to_blacklist(self, token: str, ttl: int) -> bool:
        """
        Добавить токен в черный список
        
        Args:
            token: JWT токен
            ttl: Время жизни в секундах
            
        Returns:
            bool: Успешность операции
        """
        try:
            # Добавляем токен в множество с именем "blacklisted_tokens"
            blacklist_key = f"blacklisted_token:{token}"
            return await self.set(blacklist_key, "1", ttl)
        except Exception as e:
            logger.error(f"Ошибка при добавлении токена в черный список: {str(e)}")
            return False
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Проверить, находится ли токен в черном списке
        
        Args:
            token: JWT токен
            
        Returns:
            bool: True, если токен в черном списке
        """
        try:
            blacklist_key = f"blacklisted_token:{token}"
            return await self.get(blacklist_key) is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке токена в черном списке: {str(e)}")
            return False

async def get_redis_service() -> RedisService:
    """
    Фабричная функция для создания и получения экземпляра RedisService
    
    Returns:
        RedisService: Инстанс Redis-сервиса
    """
    redis_service = RedisService()
    connected = await redis_service.is_connected()
    if not connected:
        logger.warning("Не удалось подключиться к Redis")
    return redis_service