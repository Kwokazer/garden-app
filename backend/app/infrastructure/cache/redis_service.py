# backend/app/infrastructure/cache/redis_service.py (добавляем недостающие методы)

import json
import logging
from typing import Any, Dict, List, Optional, Union
from app.utils.json_encoder import json_dumps, json_loads
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
    
    async def get(self, key: str) -> Optional[Union[str, Dict, List]]:
        """Получить значение по ключу"""
        try:
            if self.redis:
                value = await self.redis.get(key)
                if value:
                    # Пытаемся десериализовать JSON, если это не удается, возвращаем строку
                    try:
                        return json_loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value
                return None
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
                value = json_dumps(value)
                
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
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        try:
            if self.redis:
                return await self.redis.exists(key) > 0
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке существования ключа в Redis: {str(e)}")
            return False
    
    async def keys(self, pattern: str) -> List[str]:
        """Получить список ключей по паттерну"""
        try:
            if self.redis:
                return await self.redis.keys(pattern)
            return []
        except Exception as e:
            logger.error(f"Ошибка при получении ключей из Redis: {str(e)}")
            return []
    
    async def get_many(self, keys: List[str]) -> Dict[str, Optional[Any]]:
        """Получить несколько значений по ключам"""
        try:
            if not self.redis or not keys:
                return {}
            
            values = await self.redis.mget(keys)
            result = {}
            
            for i, key in enumerate(keys):
                value = values[i] if i < len(values) else None
                if value:
                    try:
                        result[key] = json_loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
                else:
                    result[key] = None
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при получении множественных значений из Redis: {str(e)}")
            return {}
    
    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Установить несколько значений"""
        try:
            if not self.redis or not items:
                return False
            
            # Подготавливаем данные для mset
            serialized_items = {}
            for key, value in items.items():
                if not isinstance(value, str):
                    serialized_items[key] = json_dumps(value)
                else:
                    serialized_items[key] = value
            
            # Устанавливаем значения
            success = await self.redis.mset(serialized_items)
            
            # Если указан TTL, устанавливаем его для каждого ключа
            if success and ttl:
                for key in items.keys():
                    await self.redis.expire(key, ttl)
            
            return success
        except Exception as e:
            logger.error(f"Ошибка при установке множественных значений в Redis: {str(e)}")
            return False
    
    async def delete_many(self, keys: List[str]) -> bool:
        """Удалить несколько ключей"""
        try:
            if not self.redis or not keys:
                return False
            
            deleted_count = await self.redis.delete(*keys)
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении множественных ключей из Redis: {str(e)}")
            return False
    
    async def clear_all(self) -> bool:
        """Очистить всю базу данных Redis"""
        try:
            if self.redis:
                await self.redis.flushdb()
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при очистке Redis: {str(e)}")
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