from typing import Dict, Any, List, Optional, Tuple
import json
from app.core.config import settings
from app.infrastructure.cache.redis_service import RedisService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class QACacheService:
    """Сервис для кеширования вопросов и ответов в Redis"""
    
    def __init__(self, redis_service: Optional[RedisService] = None):
        """
        Инициализация сервиса кеширования
        
        Args:
            redis_service: Сервис Redis (если None, будет создан новый)
        """
        self.redis = redis_service
        self.ttl = 3600  # Время жизни кеша в секундах (1 час)
        self.questions_key_prefix = "qa:question:"
        self.questions_list_key_prefix = "qa:questions:"
    
    async def get_redis(self) -> RedisService:
        """
        Получить сервис Redis
        
        Returns:
            RedisService: Сервис Redis
        """
        if self.redis is None:
            from app.infrastructure.cache.redis_service import get_redis_service
            self.redis = await get_redis_service()
        return self.redis
    
    async def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить вопрос из кеша
        
        Args:
            question_id: ID вопроса
            
        Returns:
            Optional[Dict[str, Any]]: Данные вопроса или None, если не найден в кеше
        """
        redis = await self.get_redis()
        key = f"{self.questions_key_prefix}{question_id}"
        
        cached_data = await redis.get(key)
        if cached_data:
            return cached_data
        return None
    
    async def set_question(self, question_id: int, question_data: Dict[str, Any]) -> bool:
        """
        Сохранить вопрос в кеш
        
        Args:
            question_id: ID вопроса
            question_data: Данные вопроса
            
        Returns:
            bool: True, если успешно сохранено
        """
        redis = await self.get_redis()
        key = f"{self.questions_key_prefix}{question_id}"
        
        # Сохраняем в Redis с TTL
        return await redis.set(key, question_data, expires=self.ttl)
    
    async def invalidate_question(self, question_id: int) -> bool:
        """
        Инвалидировать кеш вопроса
        
        Args:
            question_id: ID вопроса
            
        Returns:
            bool: True, если успешно инвалидировано
        """
        redis = await self.get_redis()
        key = f"{self.questions_key_prefix}{question_id}"
        
        return await redis.delete(key)
    
    async def get_questions_list(self, cache_key: str) -> Optional[Tuple[List[Dict[str, Any]], int]]:
        """
        Получить список вопросов из кеша
        
        Args:
            cache_key: Ключ кеша для списка вопросов
            
        Returns:
            Optional[Tuple[List[Dict[str, Any]], int]]: Кортеж (список вопросов, общее количество) или None
        """
        redis = await self.get_redis()
        key = f"{self.questions_list_key_prefix}{cache_key}"
        
        cached_data = await redis.get(key)
        if cached_data:
            return cached_data["items"], cached_data["total"]
        return None
    
    async def set_questions_list(self, cache_key: str, data: Tuple[List[Dict[str, Any]], int]) -> bool:
        """
        Сохранить список вопросов в кеш
        
        Args:
            cache_key: Ключ кеша для списка вопросов
            data: Кортеж (список вопросов, общее количество)
            
        Returns:
            bool: True, если успешно сохранено
        """
        redis = await self.get_redis()
        key = f"{self.questions_list_key_prefix}{cache_key}"
        
        # Сериализуем данные
        questions_list, total = data
        serialized_data = {
            "items": questions_list,
            "total": total
        }
        
        # Сохраняем в Redis с TTL
        return await redis.set(key, serialized_data, expires=self.ttl)
    
    async def invalidate_questions_list(self) -> bool:
        """
        Инвалидировать кеш списка вопросов
        
        Returns:
            bool: True, если успешно инвалидировано
        """
        redis = await self.get_redis()
        
        # Получаем все ключи списков вопросов и удаляем их
        keys = await redis.keys(f"{self.questions_list_key_prefix}*")
        if keys:
            await redis.delete(*keys)
        return True

# Предоставляем синоним класса для обратной совместимости
QACache = QACacheService 