import logging
import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# Строка подключения к базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Создаем асинхронный движок 
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # В продакшене лучше выключить
    future=True,
    pool_size=5,  # Размер пула соединений
    max_overflow=10,  # Максимальное количество дополнительных соединений, если пул исчерпан
    pool_timeout=30,  # Тайм-аут ожидания свободного соединения
    pool_recycle=1800,  # Пересоздание соединений каждые 30 минут для безопасности
    pool_pre_ping=True,  # Проверять соединение перед использованием
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,  # Не истекать объекты при коммите
    autoflush=False,  # Отключаем автоматический flush
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных в FastAPI.
    Используется в Depends() для инъекции в обработчики запросов.
    """
    session = None
    try:
        # Создаем новую сессию для каждого запроса
        session = AsyncSessionLocal()
        
        # Убеждаемся, что сессия валидна
        try:
            # Выполняем простой запрос для проверки подключения
            await session.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Ошибка при проверке соединения с БД: {str(e)}")
            # Закрываем невалидную сессию и создаем новую
            await session.close()
            session = AsyncSessionLocal()
            
        yield session
        
        # Коммитим изменения в конце запроса
        await session.commit()
    except Exception as e:
        # Откатываем изменения при ошибке
        logger.error(f"Ошибка в сессии БД: {str(e)}")
        if session:
            await session.rollback()
        raise
    finally:
        # Всегда закрываем сессию
        if session:
            await session.close()

# Отдельная функция для тестов, которая создает новую сессию с транзакцией
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения тестовой сессии базы данных.
    Используется в тестах для изоляции транзакций.
    """
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close() 