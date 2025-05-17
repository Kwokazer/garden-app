from typing import Any, Dict, List, Optional, Union, TypeVar, cast

from app.core.constants import DEFAULT_CACHE_TTL
from app.domain.schemas.plant import PlantListResponse, PlantResponse
from app.domain.schemas.plant_category import PlantCategoryResponse
from app.domain.schemas.climate_zone import ClimateZoneResponse
from app.infrastructure.cache.base_cache_service import BaseCacheService, T
from app.infrastructure.cache.redis_service import RedisService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PlantCacheService(BaseCacheService[Any]):
    """Сервис для кэширования данных о растениях"""
    
    def __init__(self, redis_service: RedisService):
        """
        Инициализация сервиса кэширования растений
        
        Args:
            redis_service: Экземпляр Redis-сервиса
        """
        super().__init__("plants", DEFAULT_CACHE_TTL)
        self.redis = redis_service
    
    # Переопределение абстрактных методов базового класса
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            Optional[Any]: Значение или None, если ключ не найден
        """
        return await self.redis.get(f"{self.prefix}:{key}")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Установить значение в кэш по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            value: Значение для сохранения
            ttl: Время жизни в секундах (если None, используется default_ttl)
            
        Returns:
            bool: True в случае успеха
        """
        return await self.redis.set(f"{self.prefix}:{key}", value, ttl or self.default_ttl)
    
    async def delete(self, key: str) -> bool:
        """
        Удалить значение из кэша по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            bool: True в случае успеха
        """
        return await self.redis.delete(f"{self.prefix}:{key}")
    
    async def exists(self, key: str) -> bool:
        """
        Проверить, существует ли ключ в кэше
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            bool: True, если ключ существует
        """
        return await self.redis.exists(f"{self.prefix}:{key}")
    
    async def clear_all(self) -> bool:
        """
        Очистить все ключи с текущим префиксом
        
        Returns:
            bool: True в случае успеха
        """
        return await self.redis.clear_all()
    
    async def get_many(self, keys: List[str]) -> Dict[str, Optional[Any]]:
        """
        Получить несколько значений из кэша по ключам
        
        Args:
            keys: Список ключей кэша (без префиксов)
            
        Returns:
            Dict[str, Optional[Any]]: Словарь {ключ: значение}
        """
        return await self.redis.get_many([f"{self.prefix}:{key}" for key in keys])
    
    async def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Установить несколько значений в кэш
        
        Args:
            items: Словарь {ключ: значение}
            ttl: Время жизни в секундах (если None, используется default_ttl)
            
        Returns:
            bool: True в случае успеха
        """
        prefixed_items = {f"{self.prefix}:{key}": value for key, value in items.items()}
        return await self.redis.set_many(prefixed_items, ttl or self.default_ttl)
    
    async def delete_many(self, keys: List[str]) -> bool:
        """
        Удалить несколько значений из кэша
        
        Args:
            keys: Список ключей (без префиксов)
            
        Returns:
            bool: True в случае успеха
        """
        return await self.redis.delete_many([f"{self.prefix}:{key}" for key in keys])
    
    # Специфические методы для работы с растениями
    
    # Ключи кэша
    def _make_plants_list_key(self, skip: int, limit: int, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Сформировать ключ для списка растений с учетом пагинации и фильтров
        
        Args:
            skip: Смещение для пагинации
            limit: Количество записей на странице
            filters: Фильтры для поиска
            
        Returns:
            str: Ключ кэша
        """
        filters_str = ""
        if filters:
            # Сортируем ключи фильтров для стабильности ключа кэша
            sorted_filters = sorted(
                [(k, str(v)) for k, v in filters.items() if v is not None],
                key=lambda x: x[0]
            )
            filters_str = "_".join([f"{k}:{v}" for k, v in sorted_filters])
        
        return f"list:skip:{skip}:limit:{limit}:{filters_str}"
    
    def _make_plant_detail_key(self, plant_id: int) -> str:
        """
        Сформировать ключ для детальной информации о растении
        
        Args:
            plant_id: ID растения
            
        Returns:
            str: Ключ кэша
        """
        return f"detail:{plant_id}"
    
    def _make_category_plants_key(self, category_id: int, skip: int, limit: int) -> str:
        """
        Сформировать ключ для списка растений в категории
        
        Args:
            category_id: ID категории
            skip: Смещение для пагинации
            limit: Количество записей на странице
            
        Returns:
            str: Ключ кэша
        """
        return f"category:{category_id}:skip:{skip}:limit:{limit}"
    
    def _make_climate_zone_plants_key(self, zone_id: int, skip: int, limit: int) -> str:
        """
        Сформировать ключ для списка растений в климатической зоне
        
        Args:
            zone_id: ID климатической зоны
            skip: Смещение для пагинации
            limit: Количество записей на странице
            
        Returns:
            str: Ключ кэша
        """
        return f"climate_zone:{zone_id}:skip:{skip}:limit:{limit}"
    
    def _make_categories_list_key(self, skip: int, limit: int) -> str:
        """
        Сформировать ключ для списка категорий
        
        Args:
            skip: Смещение для пагинации
            limit: Количество записей на странице
            
        Returns:
            str: Ключ кэша
        """
        return f"categories:skip:{skip}:limit:{limit}"
    
    def _make_climate_zones_list_key(self, skip: int, limit: int) -> str:
        """
        Сформировать ключ для списка климатических зон
        
        Args:
            skip: Смещение для пагинации
            limit: Количество записей на странице
            
        Returns:
            str: Ключ кэша
        """
        return f"climate_zones:skip:{skip}:limit:{limit}"
    
    # Методы для кэширования списков растений
    async def get_plants_list(
        self, 
        skip: int, 
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[PlantListResponse]:
        """
        Получить список растений из кэша
        
        Args:
            skip: Смещение для пагинации
            limit: Количество записей на странице
            filters: Фильтры для поиска
            
        Returns:
            Optional[PlantListResponse]: Список растений или None, если не найден в кэше
        """
        key = self._make_plants_list_key(skip, limit, filters)
        data = await self.get(key)
        
        if data:
            logger.debug(f"Получены данные о списке растений из кэша")
            return PlantListResponse.model_validate(data)
        
        return None
    
    async def set_plants_list(
        self, 
        plants_list: PlantListResponse,
        skip: int, 
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Сохранить список растений в кэш
        
        Args:
            plants_list: Список растений
            skip: Смещение для пагинации
            limit: Количество записей на странице
            filters: Фильтры для поиска
            ttl: Время жизни в секундах
            
        Returns:
            bool: True в случае успеха
        """
        key = self._make_plants_list_key(skip, limit, filters)
        logger.debug(f"Сохранение списка растений в кэш")
        return await self.set(
            key, 
            plants_list.model_dump(), 
            ttl
        )
    
    # Методы для кэширования детальной информации о растении
    async def get_plant_detail(self, plant_id: int) -> Optional[PlantResponse]:
        """
        Получить детальную информацию о растении из кэша
        
        Args:
            plant_id: ID растения
            
        Returns:
            Optional[PlantResponse]: Информация о растении или None, если не найдена в кэше
        """
        key = self._make_plant_detail_key(plant_id)
        data = await self.get(key)
        
        if data:
            logger.debug(f"Получены данные о растении {plant_id} из кэша")
            return PlantResponse.model_validate(data)
        
        return None
    
    async def set_plant_detail(
        self, 
        plant: PlantResponse,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Сохранить детальную информацию о растении в кэш
        
        Args:
            plant: Информация о растении
            ttl: Время жизни в секундах
            
        Returns:
            bool: True в случае успеха
        """
        key = self._make_plant_detail_key(plant.id)
        logger.debug(f"Сохранение информации о растении {plant.id} в кэш")
        return await self.set(
            key, 
            plant.model_dump(), 
            ttl
        )
    
    # Методы для кэширования списков растений по категории
    async def get_category_plants(
        self, 
        category_id: int,
        skip: int, 
        limit: int
    ) -> Optional[PlantListResponse]:
        """
        Получить список растений по категории из кэша
        
        Args:
            category_id: ID категории
            skip: Смещение для пагинации
            limit: Количество записей на странице
            
        Returns:
            Optional[PlantListResponse]: Список растений или None, если не найден в кэше
        """
        key = self._make_category_plants_key(category_id, skip, limit)
        data = await self.get(key)
        
        if data:
            logger.debug(f"Получены данные о растениях для категории {category_id} из кэша")
            return PlantListResponse.model_validate(data)
        
        return None
    
    async def set_category_plants(
        self, 
        category_id: int,
        plants_list: PlantListResponse,
        skip: int, 
        limit: int,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Сохранить список растений по категории в кэш
        
        Args:
            category_id: ID категории
            plants_list: Список растений
            skip: Смещение для пагинации
            limit: Количество записей на странице
            ttl: Время жизни в секундах
            
        Returns:
            bool: True в случае успеха
        """
        key = self._make_category_plants_key(category_id, skip, limit)
        logger.debug(f"Сохранение списка растений для категории {category_id} в кэш")
        return await self.set(
            key, 
            plants_list.model_dump(), 
            ttl
        )
    
    # Методы инвалидации кэша
    async def invalidate_plant_detail(self, plant_id: int) -> bool:
        """
        Инвалидировать кэш детальной информации о растении
        
        Args:
            plant_id: ID растения
            
        Returns:
            bool: True в случае успеха
        """
        key = self._make_plant_detail_key(plant_id)
        logger.debug(f"Инвалидация информации о растении {plant_id}")
        return await self.delete(key)
    
    async def invalidate_plants_lists(self) -> bool:
        """
        Инвалидировать все кэши списков растений
        
        Returns:
            bool: True в случае успеха
        """
        logger.debug("Инвалидация всех списков растений")
        keys = await self.redis.keys("list:*")
        if keys:
            success = await self.delete_many(keys)
            logger.debug(f"Удалено {len(keys)} ключей списков растений")
            return success
        return True
    
    async def invalidate_category_plants(self, category_id: int) -> bool:
        """
        Инвалидировать кэши списков растений в категории
        
        Args:
            category_id: ID категории
            
        Returns:
            bool: True в случае успеха
        """
        logger.debug(f"Инвалидация списков растений для категории {category_id}")
        keys = await self.redis.keys(f"category:{category_id}:*")
        if keys:
            success = await self.delete_many(keys)
            logger.debug(f"Удалено {len(keys)} ключей для категории {category_id}")
            return success
        return True
    
    async def invalidate_climate_zone_plants(self, zone_id: int) -> bool:
        """
        Инвалидировать кэши списков растений в климатической зоне
        
        Args:
            zone_id: ID климатической зоны
            
        Returns:
            bool: True в случае успеха
        """
        logger.debug(f"Инвалидация списков растений для климатической зоны {zone_id}")
        keys = await self.redis.keys(f"climate_zone:{zone_id}:*")
        if keys:
            success = await self.delete_many(keys)
            logger.debug(f"Удалено {len(keys)} ключей для климатической зоны {zone_id}")
            return success
        return True

# Предоставляем синоним класса для обратной совместимости
PlantCache = PlantCacheService 