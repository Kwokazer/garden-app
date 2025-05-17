import logging
import os
import smtplib
import ssl
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    Сервис для отправки электронных писем
    """
    
    def __init__(self):
        """
        Инициализация сервиса с настройками SMTP
        """
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        
        # Путь к директории с шаблонами
        self.templates_dir = settings.EMAIL_TEMPLATES_DIR or 'app/infrastructure/external/templates/email'
        
        # Инициализируем Jinja2 для шаблонов
        self.template_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # URL фронтенда для формирования ссылок
        self.frontend_url = settings.FRONTEND_URL
        
        logger.info(f"Инициализирован сервис отправки email с SMTP сервером {self.smtp_host}:{self.smtp_port}")
    
    def _get_or_create_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Получить текущий event loop или создать новый
        
        Returns:
            asyncio.AbstractEventLoop: Event loop
        """
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    async def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Отправить электронное письмо
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            html_content: HTML-содержимое письма
            
        Returns:
            bool: Успешность отправки
        """
        if settings.ENVIRONMENT == "test":
            # В тестовом окружении только логируем сообщение, не отправляем
            logger.info(f"Эмуляция отправки письма: {subject} -> {to_email}")
            return True
            
        logger.info(f"Попытка отправки письма: {subject} -> {to_email} через {self.smtp_host}:{self.smtp_port}")
            
        # Если настройки SMTP не заданы, выводим сообщение в лог и не отправляем
        if not self.smtp_host or not self.smtp_port:
            logger.warning("Настройки SMTP не заданы, отправка невозможна")
            return False
            
        try:
            # Создаем сообщение
            message = MIMEMultipart()
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = to_email
            
            # Добавляем HTML-содержимое
            message.attach(MIMEText(html_content, "html"))
            
            # MailHog не требует аутентификации и TLS
            # При работе в Docker-контейнере используем имя сервиса mailhog как хост
            smtp_host = self.smtp_host
            if smtp_host == "mailhog" and os.environ.get("DOCKER_ENV") == "true":
                smtp_host = "mailhog"  # Используем имя сервиса в Docker-сети
            
            if self.smtp_host == "mailhog":
                with smtplib.SMTP(smtp_host, self.smtp_port) as server:
                    server.sendmail(self.email_from, to_email, message.as_string())
                logger.info(f"Отправлено письмо через MailHog: {subject} -> {to_email}")
                return True
            
            # Для других SMTP серверов используем TLS и аутентификацию
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                
                server.sendmail(self.email_from, to_email, message.as_string())
            
            logger.info(f"Отправлено письмо: {subject} -> {to_email}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке письма {subject} для {to_email}: {str(e)}", exc_info=True)
            return False
    
    async def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Отправить письмо для верификации email
        
        Args:
            to_email: Email получателя
            verification_token: Токен верификации
            
        Returns:
            bool: Успешность отправки
        """
        try:
            # Формируем ссылку для верификации
            verification_url = f"{self.frontend_url}/verify-email?token={quote(verification_token)}"
            
            # Получаем шаблон
            template = self.template_env.get_template('email_verification.html')
            
            # Рендерим HTML с данными
            html_content = template.render(
                verification_url=verification_url,
                app_name=settings.APP_NAME
            )
            
            # Отправляем письмо
            return await self.send_email(
                to_email=to_email,
                subject=f"Подтверждение email для {settings.APP_NAME}",
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке письма верификации для {to_email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Отправить письмо для сброса пароля
        
        Args:
            to_email: Email получателя
            reset_token: Токен для сброса пароля
            
        Returns:
            bool: Успешность отправки
        """
        try:
            # Формируем ссылку для сброса пароля
            reset_url = f"{self.frontend_url}/reset-password?token={quote(reset_token)}"
            
            # Получаем шаблон
            template = self.template_env.get_template('password_reset.html')
            
            # Рендерим HTML с данными
            html_content = template.render(
                reset_url=reset_url,
                app_name=settings.APP_NAME
            )
            
            # Отправляем письмо
            return await self.send_email(
                to_email=to_email,
                subject=f"Сброс пароля для {settings.APP_NAME}",
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке письма сброса пароля для {to_email}: {str(e)}")
            return False
    
    async def send_notification_email(self, to_email: str, subject: str, message: str) -> bool:
        """
        Отправить общее уведомление
        
        Args:
            to_email: Email получателя
            subject: Тема уведомления
            message: Текст уведомления
            
        Returns:
            bool: Успешность отправки
        """
        try:
            # Формируем простой HTML для уведомления
            html_content = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>{subject}</h2>
                    <p>{message}</p>
                    <p>С уважением,<br>Команда {settings.APP_NAME}</p>
                </div>
            </body>
            </html>
            """
            
            # Отправляем письмо
            return await self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления для {to_email}: {str(e)}")
            return False

# Создаем глобальный экземпляр сервиса для использования через зависимости
email_service = EmailService() 