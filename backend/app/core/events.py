import logging
import time
from typing import Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.database import close_db_connection, connect_to_db, init_models
from app.infrastructure.cache.redis_service import RedisService, get_redis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Создает обработчик события запуска приложения
    
    Args:
        app: FastAPI приложение
        
    Returns:
        Callable: Функция-обработчик
    """
    async def start_app() -> None:
        """
        Выполняется при запуске приложения
        """
        logger.info("Запуск приложения")
        
        start_time = time.time()
        
        # Инициализация базы данных
        logger.info("Инициализация базы данных")
        await init_models()
        
        # Инициализация Redis
        try:
            logger.info("Инициализация Redis")
            redis_service = await get_redis_service()
            logger.info("Redis успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Redis: {str(e)}")
            # Не прерываем запуск приложения из-за проблем с Redis
        
        # Добавление событий в метрики
        app.state.start_time = start_time
        elapsed = time.time() - start_time
        logger.info(f"Приложение успешно запущено за {elapsed:.2f} секунд")
        
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Создает обработчик события остановки приложения
    
    Args:
        app: FastAPI приложение
        
    Returns:
        Callable: Функция-обработчик
    """
    async def stop_app() -> None:
        """
        Выполняется при остановке приложения
        """
        logger.info("Остановка приложения")
        
        # Закрытие Redis
        try:
            redis_service = await get_redis_service()
            await redis_service.close()
            logger.info("Соединение с Redis закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения с Redis: {str(e)}")
        
        # Закрытие базы данных
        logger.info("Закрытие соединения с базой данных")
        await close_db_connection()
        
        logger.info("Приложение успешно остановлено")
        
    return stop_app

def register_app_events(app: FastAPI) -> None:
    """
    Регистрирует обработчики событий в приложении
    
    Args:
        app: FastAPI приложение
    """
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))
