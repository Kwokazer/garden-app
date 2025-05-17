from fastapi import Depends

from app.infrastructure.external.email_service import EmailService, email_service


async def get_email_service() -> EmailService:
    """
    Получение сервиса отправки электронной почты
    
    Returns:
        EmailService: Экземпляр сервиса отправки email
    """
    return email_service 