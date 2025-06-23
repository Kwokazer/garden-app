import logging
from datetime import datetime, timedelta
from typing import List

from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.database.repositories.webinar_repository import WebinarRepository
from app.domain.models.webinar import WebinarStatus

logger = logging.getLogger(__name__)

async def get_async_session():
    """Создает новую сессию для Celery задач"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

@celery_app.task(bind=True, max_retries=3)
def activate_webinar_task(self, webinar_id: int):
    """
    Задача для смены статуса вебинара на LIVE
    """
    try:
        logger.info(f"Активация вебинара {webinar_id}")
        
        import asyncio
        result = asyncio.run(_activate_webinar_async(webinar_id))
        
        logger.info(f"Вебинар {webinar_id} успешно активирован")
        return result
        
    except Exception as exc:
        logger.error(f"Ошибка при активации вебинара {webinar_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"Повторная попытка {self.request.retries + 1}/{self.max_retries}")
            raise self.retry(exc=exc, countdown=30)
        else:
            logger.error(f"Исчерпаны попытки активации вебинара {webinar_id}")
            return {"status": "failed", "webinar_id": webinar_id, "error": str(exc)}

async def _activate_webinar_async(webinar_id: int):
    """Асинхронная функция для активации вебинара"""
    session = AsyncSessionLocal()
    try:
        webinar_repo = WebinarRepository(session)
        
        # Получаем вебинар
        webinar = await webinar_repo.get_by_id(webinar_id)
        if not webinar:
            raise ValueError(f"Вебинар {webinar_id} не найден")
        
        # Проверяем, что можно активировать
        if webinar.status != WebinarStatus.SCHEDULED:
            logger.warning(f"Вебинар {webinar_id} уже в статусе {webinar.status.value}")
            return {"status": "already_processed", "webinar_id": webinar_id}
        
        # Меняем статус на LIVE
        await webinar_repo.update(webinar_id, {
            "status": WebinarStatus.LIVE
        })
        
        # Создаем Jitsi комнату, если её нет
        if not webinar.room_name:
            room_name = f"webinar_{webinar_id}_{int(datetime.utcnow().timestamp())}"
            await webinar_repo.update(webinar_id, {
                "room_name": room_name
            })
        
        await session.commit()

        return {
            "status": "activated",
            "webinar_id": webinar_id
        }
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

@celery_app.task
def check_and_activate_webinars():
    """
    Периодическая задача для проверки и активации вебинаров
    """
    try:
        logger.info("Проверка вебинаров для активации")
        
        import asyncio
        result = asyncio.run(_check_and_activate_webinars_async())
        
        logger.info(f"Проверка завершена. Активировано: {result['activated_count']}")
        return result
        
    except Exception as exc:
        logger.error(f"Ошибка при проверке вебинаров: {exc}")
        return {"status": "error", "error": str(exc)}

async def _check_and_activate_webinars_async():
    """Проверка и активация вебинаров, время которых наступило"""
    session = AsyncSessionLocal()
    try:
        webinar_repo = WebinarRepository(session)
        
        # Получаем текущее время
        now = datetime.utcnow()
        
        # Находим вебинары, которые должны быть активированы
        webinars_to_activate = await webinar_repo.get_webinars_to_activate(now)
        
        activated_count = 0
        for webinar in webinars_to_activate:
            try:
                # Меняем статус на LIVE
                await webinar_repo.update(webinar.id, {
                    "status": WebinarStatus.LIVE
                })
                
                # Создаем Jitsi комнату, если её нет
                if not webinar.room_name:
                    room_name = f"webinar_{webinar.id}_{int(now.timestamp())}"
                    await webinar_repo.update(webinar.id, {
                        "room_name": room_name
                    })
                
                activated_count += 1
                logger.info(f"Активирован вебинар {webinar.id}: {webinar.title}")
                
            except Exception as e:
                logger.error(f"Ошибка при активации вебинара {webinar.id}: {e}")
        
        await session.commit()

        return {
            "status": "success",
            "checked_at": now.isoformat(),
            "found_count": len(webinars_to_activate),
            "activated_count": activated_count
        }
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

@celery_app.task
def schedule_webinar_activation(webinar_id: int, activation_time_iso: str):
    """
    Планирование активации конкретного вебинара в определенное время
    """
    try:
        activation_time = datetime.fromisoformat(activation_time_iso.replace('Z', '+00:00'))
        
        # Планируем задачу активации
        celery_app.send_task(
            'app.tasks.webinar_tasks.activate_webinar_task',
            args=[webinar_id],
            eta=activation_time,
            task_id=f"webinar_activate_{webinar_id}"
        )
        
        logger.info(f"Запланирована активация вебинара {webinar_id} на {activation_time}")
        return {"status": "scheduled", "webinar_id": webinar_id}
        
    except Exception as exc:
        logger.error(f"Ошибка при планировании активации вебинара {webinar_id}: {exc}")
        return {"status": "error", "error": str(exc)}

@celery_app.task
def cancel_webinar_activation(webinar_id: int):
    """
    Отмена запланированной активации вебинара
    """
    try:
        celery_app.control.revoke(f"webinar_activate_{webinar_id}", terminate=True)
        logger.info(f"Отменена активация вебинара {webinar_id}")
        return {"status": "cancelled", "webinar_id": webinar_id}
    except Exception as exc:
        logger.error(f"Ошибка при отмене активации вебинара {webinar_id}: {exc}")
        return {"status": "error", "error": str(exc)}
