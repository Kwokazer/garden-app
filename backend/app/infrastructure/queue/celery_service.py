from typing import Any, Callable, Dict, List, Optional, Union
import time
from functools import wraps

from celery import Celery
from celery.result import AsyncResult

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CeleryService:
    """
    Сервис для работы с асинхронными задачами с использованием Celery
    """
    
    def __init__(self):
        """
        Инициализация Celery-сервиса
        """
        self.broker_url = settings.CELERY_BROKER_URL
        self.result_backend = settings.CELERY_RESULT_BACKEND
        
        self.app = Celery(
            'app',
            broker=self.broker_url,
            backend=self.result_backend,
            include=['app.tasks']
        )
        
        # Настройки Celery
        self.app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='Europe/Moscow',
            enable_utc=True,
            task_track_started=True,
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            task_reject_on_worker_lost=True,
            task_time_limit=3600,  # 1 час
            task_soft_time_limit=3600,  # 1 час
        )
        
        logger.info(f"Инициализирован Celery-сервис с брокером {self.broker_url}")
    
    def get_task_result(self, task_id: str) -> AsyncResult:
        """
        Получить результат задачи по ID
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            AsyncResult: Объект результата задачи
        """
        return AsyncResult(task_id, app=self.app)
    
    def wait_for_result(self, task_id: str, timeout: Optional[int] = None) -> Any:
        """
        Дождаться результата задачи
        
        Args:
            task_id: Идентификатор задачи
            timeout: Таймаут ожидания в секундах
            
        Returns:
            Any: Результат выполнения задачи
        """
        return self.get_task_result(task_id).get(timeout=timeout)
    
    def get_task_status(self, task_id: str) -> str:
        """
        Получить статус задачи
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            str: Статус задачи (PENDING, STARTED, RETRY, FAILURE, SUCCESS)
        """
        return self.get_task_result(task_id).status
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> None:
        """
        Отменить задачу
        
        Args:
            task_id: Идентификатор задачи
            terminate: Принудительно завершить уже запущенную задачу
        """
        self.app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Отменена задача {task_id} (terminate={terminate})")
    
    def is_task_successful(self, task_id: str) -> bool:
        """
        Проверить, успешно ли выполнена задача
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            bool: True, если задача выполнена успешно
        """
        result = self.get_task_result(task_id)
        return result.successful()
    
    def is_task_failed(self, task_id: str) -> bool:
        """
        Проверить, завершилась ли задача с ошибкой
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            bool: True, если задача завершилась с ошибкой
        """
        result = self.get_task_result(task_id)
        return result.failed()
    
    def retry_task(self, task_id: str) -> Optional[str]:
        """
        Повторить выполнение задачи
        
        Args:
            task_id: Идентификатор задачи
            
        Returns:
            Optional[str]: Идентификатор новой задачи или None, если повтор невозможен
        """
        result = self.get_task_result(task_id)
        
        if result.task_name is None:
            logger.error(f"Невозможно повторить задачу {task_id}: неизвестный тип задачи")
            return None
            
        try:
            task = self.app.tasks[result.task_name]
            args = result.args or []
            kwargs = result.kwargs or {}
            
            # Запускаем задачу повторно
            new_task = task.apply_async(args=args, kwargs=kwargs)
            logger.info(f"Задача {task_id} перезапущена как {new_task.id}")
            return new_task.id
        except Exception as e:
            logger.error(f"Ошибка при повторе задачи {task_id}: {str(e)}")
            return None
    
    def task_with_retry(
        self,
        max_retries: int = 3,
        retry_delay: int = 60,
        retry_backoff: bool = True,
        retry_jitter: bool = True,
        **options
    ):
        """
        Декоратор для задач с автоматическими повторными попытками
        
        Args:
            max_retries: Максимальное количество повторов
            retry_delay: Задержка между повторами в секундах
            retry_backoff: Использовать экспоненциальное увеличение задержки
            retry_jitter: Добавлять случайность к задержке
            **options: Дополнительные параметры для задачи
            
        Returns:
            Callable: Декоратор задачи
        """
        def decorator(func):
            @self.app.task(
                bind=True,
                max_retries=max_retries,
                default_retry_delay=retry_delay,
                autoretry_for=(Exception,),
                retry_backoff=retry_backoff,
                retry_backoff_max=600,  # Максимальная задержка - 10 минут
                retry_jitter=retry_jitter,
                **options
            )
            @wraps(func)
            def wrapper(self_task, *args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    logger.warning(
                        f"Задача {self_task.name} будет повторена (попытка {self_task.request.retries + 1}/{max_retries}). Ошибка: {str(exc)}"
                    )
                    raise self_task.retry(exc=exc)
            return wrapper
        return decorator

# Создаем глобальный экземпляр сервиса для использования через зависимости
celery_service = CeleryService() 