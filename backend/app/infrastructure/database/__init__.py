from .connection import engine, get_db, get_test_db


async def init_models():
    """
    Инициализирует базу данных при запуске приложения.
    Можно использовать для проверки соединения или создания таблиц, если требуется.
    """
    # В продакшене таблицы создаются через миграции Alembic,
    # но здесь можно выполнить дополнительные проверки
    # или инициализацию начальных данных
    from app.domain.models.base import Base

    # Проверяем соединение с базой данных
    async with engine.begin() as conn:
        # Если нужно создать таблицы (для разработки/тестирования):
        # await conn.run_sync(Base.metadata.create_all)
        # В продакшене лучше использовать миграции
        pass

async def close_db_connection():
    """
    Закрывает соединение с базой данных при завершении работы приложения
    """
    await engine.dispose()

__all__ = [
    "get_db", 
    "get_test_db",
    "init_models",
    "close_db_connection"
] 