"""
Конфигурация pytest для тестов Garden API
"""
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.domain.models.base import Base
from app.infrastructure.database import get_db
from app.core.config import settings

# Настройки тестовой базы данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создаем тестовый движок
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Создаем фабрику тестовых сессий
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Убираем устаревшую фикстуру event_loop - pytest-asyncio управляет этим автоматически


@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Создает тестовую базу данных"""
    import os

    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Удаляем таблицы и закрываем движок
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Закрываем движок
    await test_engine.dispose()

    # Удаляем файл тестовой базы данных
    test_db_file = "./test.db"
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print(f"✅ Удален файл тестовой базы данных: {test_db_file}")


@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Создает тестовую сессию базы данных с автоматической очисткой"""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        # Откатываем транзакцию (это очищает все изменения в тесте)
        await session.close()
        await transaction.rollback()
        await connection.close()

        # Дополнительная очистка: удаляем все данные из всех таблиц
        async with test_engine.begin() as cleanup_conn:
            # Получаем все таблицы и очищаем их
            for table in reversed(Base.metadata.sorted_tables):
                await cleanup_conn.execute(table.delete())


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создает тестовый HTTP клиент"""
    from httpx import ASGITransport

    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Создает тестового администратора"""
    from app.domain.models.user import User
    from app.domain.models.role import Role
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Создаем роль администратора
    admin_role = Role(name="admin", description="Администратор")
    db_session.add(admin_role)
    await db_session.flush()
    
    # Создаем пользователя-администратора
    hashed_password = pwd_context.hash("Admin123!")
    admin = User(
        email="admin@test.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True
    )
    admin.roles.append(admin_role)
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    return admin


@pytest_asyncio.fixture
async def plant_expert_user(db_session: AsyncSession):
    """Создает тестового эксперта по растениям"""
    from app.domain.models.user import User
    from app.domain.models.role import Role
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Создаем роль эксперта
    expert_role = Role(name="plant_expert", description="Эксперт по растениям")
    db_session.add(expert_role)
    await db_session.flush()
    
    # Создаем пользователя-эксперта
    hashed_password = pwd_context.hash("Expert123!")
    expert = User(
        email="expert@test.com",
        username="expert",
        first_name="Plant",
        last_name="Expert",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True
    )
    expert.roles.append(expert_role)
    db_session.add(expert)
    await db_session.commit()
    await db_session.refresh(expert)
    
    return expert


@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession):
    """Создает обычного пользователя"""
    from app.domain.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    hashed_password = pwd_context.hash("User123!")
    user = User(
        email="user@test.com",
        username="user",
        first_name="Regular",
        last_name="User",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def test_plant(db_session: AsyncSession):
    """Создает тестовое растение"""
    from app.domain.models.plant import Plant, PlantType

    plant = Plant(
        name="Тестовое растение",
        latin_name="Testus plantus",
        description="Описание тестового растения",
        plant_type=PlantType.FLOWER,
        popularity_score=100
    )
    db_session.add(plant)
    await db_session.commit()
    await db_session.refresh(plant)

    return plant


@pytest_asyncio.fixture
async def auth_headers_admin(client: AsyncClient, admin_user):
    """Получает заголовки авторизации для администратора"""
    login_data = {
        "email": "admin@test.com",
        "password": "Admin123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def auth_headers_expert(client: AsyncClient, plant_expert_user):
    """Получает заголовки авторизации для эксперта"""
    login_data = {
        "email": "expert@test.com",
        "password": "Expert123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest_asyncio.fixture
async def auth_headers_user(client: AsyncClient, regular_user):
    """Получает заголовки авторизации для обычного пользователя"""
    login_data = {
        "email": "user@test.com",
        "password": "User123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
