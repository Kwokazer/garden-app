import logging

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.common.errors import register_exception_handlers
from app.api.v1.api import api_router
from app.application.dependencies import get_redis_service
from app.core.config import settings
from app.infrastructure.database import close_db_connection, init_models

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API для садоводов и любителей растений",
    version="0.1.0"
)

# Регистрация обработчиков исключений
register_exception_handlers(app)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,  # Используем свойство, возвращающее список
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)

# События приложения для инициализации и закрытия ресурсов
@app.on_event("startup")
async def startup_event():
    """
    Инициализация ресурсов при запуске приложения
    """
    logger.info("Инициализация приложения...")
    
    # Инициализация базы данных
    await init_models()
    
    # Инициализация Redis
    redis_service = await get_redis_service()
    
    logger.info("Приложение успешно инициализировано")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Освобождение ресурсов при завершении работы приложения
    """
    logger.info("Завершение работы приложения...")
    
    # Закрытие подключения к Redis
    redis_service = await get_redis_service()
    await redis_service.close()
    
    # Закрытие подключения к базе данных
    await close_db_connection()
    
    logger.info("Ресурсы успешно освобождены")

# Глобальные эндпоинты
@app.get(f"{settings.API_V1_STR}/healthz")
async def health_check():
    """
    Проверка работоспособности API
    """
    return {"status": "ok"}


@app.get("/")
async def root():
    """
    Корневой эндпоинт, перенаправляющий на API v1
    """
    return {
        "message": "Добро пожаловать в Garden API!",
        "api_v1": f"{settings.API_V1_STR}",
        "docs": "/docs",
        "version": "0.1.0",
    }


# Для запуска приложения из командной строки
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
