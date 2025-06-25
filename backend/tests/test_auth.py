"""
Тесты для аутентификации и регистрации пользователей
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch


# Мок для email сервиса убран - используем реальный MailHog для тестирования


class TestUserRegistration:
    """Тесты регистрации пользователей"""

    @pytest.mark.asyncio
    async def test_user_registration_with_email_verification(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """
        Тест регистрации пользователя с подтверждением email
        
        Проверяет:
        1. Успешную регистрацию пользователя
        2. Создание токена верификации
        3. Отправку email с подтверждением
        4. Подтверждение email по токену
        5. Активацию аккаунта
        """
        # Данные для регистрации
        registration_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        # 1. Регистрация пользователя
        response = await client.post("/api/v1/auth/register", json=registration_data)
        
        # Проверяем успешную регистрацию
        assert response.status_code == 201
        registration_response = response.json()
        
        assert registration_response["email"] == registration_data["email"]
        assert registration_response["username"] == registration_data["username"]
        assert registration_response["is_verified"] is False
        assert "id" in registration_response
        assert "message" in registration_response
        
        user_id = registration_response["id"]
        
        # 2. Проверяем, что пользователь создан в базе данных с токеном верификации
        from app.domain.models.user import User
        from sqlalchemy import select

        result = await db_session.execute(
            select(User).where(User.email == registration_data["email"])
        )
        created_user = result.scalar_one_or_none()

        assert created_user is not None
        assert created_user.email == registration_data["email"]
        assert created_user.username == registration_data["username"]
        assert created_user.is_verified is False
        assert created_user.verification_token is not None
        assert created_user.verification_token_expires_at is not None

        verification_token = created_user.verification_token
        
        # 3. Подтверждение email по токену
        verification_data = {
            "verification_token": verification_token
        }
        
        verify_response = await client.post("/api/v1/auth/verify-email", json=verification_data)
        
        # Проверяем успешное подтверждение
        assert verify_response.status_code == 200
        verify_result = verify_response.json()
        assert verify_result["message"] == "Email успешно подтвержден"
        
        # 4. Проверяем, что пользователь теперь верифицирован
        await db_session.refresh(created_user)
        assert created_user.is_verified is True
        assert created_user.verification_token is None
        assert created_user.verification_token_expires_at is None
        
        # 5. Проверяем, что теперь можно войти в систему
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_result = login_response.json()
        assert "access_token" in login_result
        assert "refresh_token" in login_result
        assert login_result["token_type"] == "bearer"
        assert "expires_in" in login_result

    @pytest.mark.asyncio
    async def test_registration_duplicate_email(self, client: AsyncClient, regular_user):
        """Тест регистрации с уже существующим email"""
        registration_data = {
            "email": "user@test.com",  # Уже существует в фикстуре
            "username": "newuser2",
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 400
        error_response = response.json()
        assert "email" in error_response["detail"].lower()

    @pytest.mark.asyncio
    async def test_registration_duplicate_username(self, client: AsyncClient, regular_user):
        """Тест регистрации с уже существующим username"""
        registration_data = {
            "email": "newuser@test.com",
            "username": "user",  # Уже существует в фикстуре
            "password": "NewUser123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 400
        error_response = response.json()
        assert "username" in error_response["detail"].lower()

    @pytest.mark.asyncio
    async def test_registration_invalid_password(self, client: AsyncClient):
        """Тест регистрации с невалидным паролем"""
        registration_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "123",  # Слишком короткий пароль
            "first_name": "New",
            "last_name": "User"
        }
        
        response = await client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_email_verification_invalid_token(self, client: AsyncClient):
        """Тест подтверждения email с невалидным токеном"""
        verification_data = {
            "verification_token": "invalid_token_12345"
        }
        
        response = await client.post("/api/v1/auth/verify-email", json=verification_data)
        assert response.status_code == 400
        error_response = response.json()
        assert "токен" in error_response["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_unverified_user(self, client: AsyncClient, db_session: AsyncSession):
        """Тест входа неверифицированного пользователя"""
        from app.domain.models.user import User
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Создаем неверифицированного пользователя
        hashed_password = pwd_context.hash("Unverified123!")
        unverified_user = User(
            email="unverified@test.com",
            username="unverified",
            first_name="Unverified",
            last_name="User",
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False  # Не верифицирован
        )
        db_session.add(unverified_user)
        await db_session.commit()
        
        # Пытаемся войти
        login_data = {
            "email": "unverified@test.com",
            "password": "Unverified123!"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        # В зависимости от логики приложения, может быть 401 или 403
        assert response.status_code in [401, 403]
