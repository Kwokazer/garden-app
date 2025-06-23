from celery import Celery
from app.core.config import settings

# Создание Celery приложения
celery_app = Celery(
    "garden",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=[
        "app.tasks.webinar_tasks",
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    # Часовой пояс
    timezone='UTC',
    enable_utc=True,
    
    # Настройки задач
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Настройки результатов
    result_expires=3600,  # Результаты хранятся 1 час
    
    # Настройки маршрутизации
    task_routes={
        'app.tasks.webinar_tasks.*': {'queue': 'webinar'},
    },
    
    # Настройки повторных попыток
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Настройки beat (планировщика)
    beat_schedule={
        'check-webinars-to-go-live': {
            'task': 'app.tasks.webinar_tasks.check_and_activate_webinars',
            'schedule': 60.0,  # Каждые 60 секунд
        },
    },
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks()
