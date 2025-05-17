"""
Задачи для асинхронной отправки Email
"""
from typing import List, Dict, Any, Optional

from app.infrastructure.external.email_service import email_service
from app.infrastructure.queue.celery_service import celery_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

@celery_service.task_with_retry(
    max_retries=5,
    retry_delay=60,
    name="tasks.send_email"
)
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Асинхронная задача отправки email
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        html_content: HTML-содержимое письма
        
    Returns:
        bool: Успешность отправки
    """
    logger.info(f"Запущена асинхронная задача отправки email: {subject} -> {to_email}")
    # Используем синхронную версию метода для работы в Celery
    loop = email_service._get_or_create_event_loop()
    result = loop.run_until_complete(
        email_service.send_email(to_email=to_email, subject=subject, html_content=html_content)
    )
    return result

@celery_service.task_with_retry(
    max_retries=3,
    retry_delay=120,
    name="tasks.send_bulk_emails"
)
def send_bulk_emails(emails: List[Dict[str, Any]], batch_size: int = 50) -> Dict[str, int]:
    """
    Асинхронная задача массовой отправки email
    
    Args:
        emails: Список словарей с параметрами писем (to_email, subject, html_content)
        batch_size: Размер пакета для отправки
        
    Returns:
        Dict[str, int]: Статистика отправки (total, sent, failed)
    """
    logger.info(f"Запущена асинхронная задача массовой отправки писем: {len(emails)} писем")
    
    results = {
        "total": len(emails),
        "sent": 0,
        "failed": 0
    }
    
    loop = email_service._get_or_create_event_loop()
    
    # Разбиваем на пакеты для избежания перегрузки SMTP сервера
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
        
        for email_data in batch:
            to_email = email_data.get("to_email")
            subject = email_data.get("subject")
            html_content = email_data.get("html_content")
            
            if not all([to_email, subject, html_content]):
                logger.warning(f"Пропущено письмо из-за неполных данных: {email_data}")
                results["failed"] += 1
                continue
            
            try:
                success = loop.run_until_complete(
                    email_service.send_email(
                        to_email=to_email,
                        subject=subject,
                        html_content=html_content
                    )
                )
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"Ошибка при отправке email для {to_email}: {str(e)}")
                results["failed"] += 1
    
    logger.info(f"Статистика массовой отправки писем: {results}")
    return results

@celery_service.task_with_retry(
    max_retries=5,
    retry_delay=60,
    name="tasks.send_verification_email"
)
def send_verification_email(to_email: str, verification_token: str) -> bool:
    """
    Асинхронная задача отправки письма верификации
    
    Args:
        to_email: Email получателя
        verification_token: Токен для верификации
        
    Returns:
        bool: Успешность отправки
    """
    logger.info(f"Запущена асинхронная задача отправки письма верификации для {to_email}")
    loop = email_service._get_or_create_event_loop()
    result = loop.run_until_complete(
        email_service.send_verification_email(to_email=to_email, verification_token=verification_token)
    )
    return result

@celery_service.task_with_retry(
    max_retries=5,
    retry_delay=60,
    name="tasks.send_password_reset_email"
)
def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Асинхронная задача отправки письма для сброса пароля
    
    Args:
        to_email: Email получателя
        reset_token: Токен для сброса пароля
        
    Returns:
        bool: Успешность отправки
    """
    logger.info(f"Запущена асинхронная задача отправки письма сброса пароля для {to_email}")
    loop = email_service._get_or_create_event_loop()
    result = loop.run_until_complete(
        email_service.send_password_reset_email(to_email=to_email, reset_token=reset_token)
    )
    return result 