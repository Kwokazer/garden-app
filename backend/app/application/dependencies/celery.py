from fastapi import Depends

from app.infrastructure.queue.celery_service import CeleryService, celery_service


async def get_celery_service() -> CeleryService:
    """
    Получение сервиса асинхронных задач Celery
    
    Returns:
        CeleryService: Экземпляр Celery-сервиса
    """
    return celery_service 