"""
Файл-алиас для совместимости с кодом, использующим название redis_cache.py
"""

from .redis_service import RedisService as RedisCache

__all__ = ["RedisCache"] 