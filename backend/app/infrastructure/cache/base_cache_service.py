from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union

from app.core.constants import DEFAULT_CACHE_TTL
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class BaseCacheService(ABC, Generic[T]):
    """
    Абстрактный базовый класс для всех сервисов кэширования
    
    Generic параметр T представляет тип данных для кэширования
    """
    
    def __init__(self, prefix: str, default_ttl: int = DEFAULT_CACHE_TTL):
        """
        Инициализация базового кэш-сервиса
        
        Args:
            prefix: Префикс для ключей кэша (используется для группировки)
            default_ttl: Время жизни кэша по умолчанию в секундах
        """
        self.prefix = prefix
        self.default_ttl = default_ttl
        
    def _format_key(self, key: str) -> str:
        """
        Форматирование ключа кэша с префиксом
        
        Args:
            key: Базовый ключ
            
        Returns:
            str: Отформатированный ключ с префиксом
        """
        return f"{self.prefix}:{key}"
    
    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """
        Получить значение из кэша по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            Optional[T]: Значение или None, если ключ не найден
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """
        Установить значение в кэш по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            value: Значение для сохранения
            ttl: Время жизни в секундах (если None, используется default_ttl)
            
        Returns:
            bool: True в случае успеха
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Удалить значение из кэша по ключу
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            bool: True в случае успеха
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Проверить, существует ли ключ в кэше
        
        Args:
            key: Ключ кэша (без префикса)
            
        Returns:
            bool: True, если ключ существует
        """
        pass
    
    @abstractmethod
    async def clear_all(self) -> bool:
        """
        Очистить все ключи с текущим префиксом
        
        Returns:
            bool: True в случае успеха
        """
        pass
    
    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, Optional[T]]:
        """
        Получить несколько значений из кэша по ключам
        
        Args:
            keys: Список ключей кэша (без префиксов)
            
        Returns:
            Dict[str, Optional[T]]: Словарь {ключ: значение}
        """
        pass
    
    @abstractmethod
    async def set_many(self, items: Dict[str, T], ttl: Optional[int] = None) -> bool:
        """
        Установить несколько значений в кэш
        
        Args:
            items: Словарь {ключ: значение}
            ttl: Время жизни в секундах (если None, используется default_ttl)
            
        Returns:
            bool: True в случае успеха
        """
        pass
    
    @abstractmethod
    async def delete_many(self, keys: List[str]) -> bool:
        """
        Удалить несколько значений из кэша
        
        Args:
            keys: Список ключей (без префиксов)
            
        Returns:
            bool: True в случае успеха
        """
        pass 