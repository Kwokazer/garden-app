import os
from typing import Any, Dict, List, Optional, Set

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Основные настройки приложения
    APP_NAME: str = "Garden API"  # Переименовано из PROJECT_NAME в APP_NAME
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development, testing, production
    API_V1_STR: str = "/api/v1"
    
    # URL фронтенда для формирования ссылок в письмах
    FRONTEND_URL: str = "http://localhost:3000"


    # Настройки Jitsi
    JITSI_API_URL: str = "https://jitsi.garden.local:8443"  # HTTPS порт
    JITSI_HTTP_URL: str = "http://jitsi.garden.local:8000"  # HTTP порт (может потребоваться для некоторых операций)
    JITSI_DOMAIN: str = "meet.jitsi"
    JITSI_APP_ID: str = "garden_app"
    JITSI_APP_SECRET: str = "jwt_secret_for_garden_app_123"

    # PostgreSQL
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_ROUTES: Dict[str, Dict[str, str]] = {
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.*": {"queue": "default"},
    }
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS - принимаем как строку
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    VK_CLIENT_ID: Optional[str] = None
    VK_CLIENT_SECRET: Optional[str] = None
    VK_REDIRECT_URI: Optional[str] = None

    YANDEX_CLIENT_ID: Optional[str] = None
    YANDEX_CLIENT_SECRET: Optional[str] = None
    YANDEX_REDIRECT_URI: Optional[str] = None

    # Почта
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "Garden <noreply@example.com>"
    EMAIL_TEMPLATES_DIR: str = "app/infrastructure/external/templates/email"

    # Хранение файлов
    STORAGE_TYPE: str = "local"  # local, s3, cloud_storage
    STORAGE_LOCAL_PATH: str = "./uploads"
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """
        Получить список разрешенных источников CORS
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def PROJECT_NAME(self) -> str:
        """
        Для обратной совместимости с кодом, использующим PROJECT_NAME
        """
        return self.APP_NAME

    @property
    def ALGORITHM(self) -> str:
        """
        Для обратной совместимости с кодом, использующим ALGORITHM
        """
        return self.JWT_ALGORITHM

    @property
    def SECRET_KEY(self) -> str:
        """
        Для обратной совместимости с кодом, использующим SECRET_KEY
        """
        return self.JWT_SECRET_KEY

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Получить строку подключения к PostgreSQL в формате SQLAlchemy
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_oauth_config(self, provider: str) -> Dict[str, str]:
        """
        Получить конфигурацию OAuth провайдера
        
        Args:
            provider: Название провайдера (google, vk, yandex)
            
        Returns:
            Dict[str, str]: Словарь с конфигурацией провайдера
        """
        if provider == "google":
            return {
                "client_id": self.GOOGLE_CLIENT_ID,
                "client_secret": self.GOOGLE_CLIENT_SECRET,
                "redirect_uri": self.GOOGLE_REDIRECT_URI,
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "scope": "openid email profile"
            }
        elif provider == "vk":
            return {
                "client_id": self.VK_CLIENT_ID,
                "client_secret": self.VK_CLIENT_SECRET,
                "redirect_uri": self.VK_REDIRECT_URI,
                "auth_url": "https://oauth.vk.com/authorize",
                "token_url": "https://oauth.vk.com/access_token",
                "userinfo_url": "https://api.vk.com/method/users.get",
                "scope": "email,photos"
            }
        elif provider == "yandex":
            return {
                "client_id": self.YANDEX_CLIENT_ID,
                "client_secret": self.YANDEX_CLIENT_SECRET, 
                "redirect_uri": self.YANDEX_REDIRECT_URI,
                "auth_url": "https://oauth.yandex.ru/authorize",
                "token_url": "https://oauth.yandex.ru/token",
                "userinfo_url": "https://login.yandex.ru/info",
                "scope": "login:email login:info login:avatar"
            }
        else:
            raise ValueError(f"Неизвестный OAuth провайдер: {provider}")

    # Настройки модели
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Игнорировать дополнительные переменные окружения
    }


settings = Settings()
