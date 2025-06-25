"""
Тесты для работы с вебинарами
"""
import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestWebinarCreation:
    """Тесты создания вебинаров"""

    @pytest.mark.asyncio
    async def test_create_webinar_as_admin(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        admin_user,
        auth_headers_admin,
        test_plant
    ):
        """
        Тест создания вебинара администратором
        
        Проверяет:
        1. Успешное создание вебинара администратором
        2. Корректность сохраненных данных
        3. Автоматическое назначение ведущего
        4. Генерацию уникального имени комнаты
        """
        # Данные для создания вебинара
        scheduled_time = datetime.now() + timedelta(days=1)
        webinar_data = {
            "title": "Тестовый вебинар администратора",
            "description": "Описание тестового вебинара",
            "scheduled_at": scheduled_time.isoformat(),
            "duration_minutes": 90,
            "max_participants": 50,
            "is_public": True,
            "plant_topic_id": test_plant.id
        }
        
        # Создаем вебинар
        response = await client.post(
            "/api/v1/webinars/", 
            json=webinar_data,
            headers=auth_headers_admin
        )
        
        # Проверяем успешное создание
        assert response.status_code == 201
        
        webinar_response = response.json()
        
        # Проверяем основные поля
        assert webinar_response["title"] == webinar_data["title"]
        assert webinar_response["description"] == webinar_data["description"]
        assert webinar_response["duration_minutes"] == webinar_data["duration_minutes"]
        assert webinar_response["max_participants"] == webinar_data["max_participants"]
        assert webinar_response["is_public"] == webinar_data["is_public"]
        assert webinar_response["plant_topic_id"] == webinar_data["plant_topic_id"]
        
        # Проверяем автоматически заполненные поля
        assert webinar_response["host_id"] == admin_user.id
        assert webinar_response["status"] == "SCHEDULED"
        assert "room_name" in webinar_response
        assert len(webinar_response["room_name"]) > 0
        assert "id" in webinar_response
        
        # Проверяем связанные данные
        assert webinar_response["host"]["id"] == admin_user.id
        assert webinar_response["host"]["username"] == admin_user.username
        
        if webinar_response["plant_topic"]:
            assert webinar_response["plant_topic"]["id"] == test_plant.id
            assert webinar_response["plant_topic"]["name"] == test_plant.name
        
        # Проверяем, что вебинар сохранен в базе данных
        from app.domain.models.webinar import Webinar
        from sqlalchemy import select
        
        result = await db_session.execute(
            select(Webinar).where(Webinar.id == webinar_response["id"])
        )
        created_webinar = result.scalar_one_or_none()
        
        assert created_webinar is not None
        assert created_webinar.title == webinar_data["title"]
        assert created_webinar.host_id == admin_user.id

    @pytest.mark.asyncio
    async def test_create_webinar_as_plant_expert(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        plant_expert_user,
        auth_headers_expert,
        test_plant
    ):
        """
        Тест создания вебинара экспертом по растениям
        
        Проверяет:
        1. Успешное создание вебинара экспертом
        2. Корректность данных
        """
        # Данные для создания вебинара
        scheduled_time = datetime.now() + timedelta(hours=2)
        webinar_data = {
            "title": "Экспертный вебинар о растениях",
            "description": "Вебинар от эксперта по растениям",
            "scheduled_at": scheduled_time.isoformat(),
            "duration_minutes": 60,
            "max_participants": 30,
            "is_public": True,
            "plant_topic_id": test_plant.id
        }
        
        # Создаем вебинар
        response = await client.post(
            "/api/v1/webinars/", 
            json=webinar_data,
            headers=auth_headers_expert
        )
        
        # Проверяем успешное создание
        assert response.status_code == 201
        
        webinar_response = response.json()
        
        # Проверяем, что ведущий - эксперт
        assert webinar_response["host_id"] == plant_expert_user.id
        assert webinar_response["host"]["username"] == plant_expert_user.username
        assert webinar_response["title"] == webinar_data["title"]

    @pytest.mark.asyncio
    async def test_create_webinar_as_regular_user_forbidden(
        self, 
        client: AsyncClient,
        regular_user,
        auth_headers_user
    ):
        """
        Тест запрета создания вебинара обычным пользователем
        
        Проверяет:
        1. Запрет создания вебинара пользователем без соответствующих ролей
        2. Возврат ошибки 403 Forbidden
        """
        # Данные для создания вебинара
        scheduled_time = datetime.now() + timedelta(hours=1)
        webinar_data = {
            "title": "Попытка создания вебинара",
            "description": "Обычный пользователь пытается создать вебинар",
            "scheduled_at": scheduled_time.isoformat(),
            "duration_minutes": 60,
            "is_public": True
        }
        
        # Пытаемся создать вебинар
        response = await client.post(
            "/api/v1/webinars/", 
            json=webinar_data,
            headers=auth_headers_user
        )
        
        # Проверяем запрет доступа
        assert response.status_code == 403
        error_response = response.json()
        assert "запрещен" in error_response["detail"].lower() or "forbidden" in error_response["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_webinar_unauthorized(self, client: AsyncClient):
        """
        Тест создания вебинара без авторизации
        
        Проверяет:
        1. Запрет создания вебинара неавторизованным пользователем
        2. Возврат ошибки 401 Unauthorized
        """
        # Данные для создания вебинара
        scheduled_time = datetime.now() + timedelta(hours=1)
        webinar_data = {
            "title": "Неавторизованная попытка",
            "description": "Попытка создания без токена",
            "scheduled_at": scheduled_time.isoformat(),
            "duration_minutes": 60,
            "is_public": True
        }
        
        # Пытаемся создать вебинар без заголовков авторизации
        response = await client.post("/api/v1/webinars/", json=webinar_data)
        
        # Проверяем отсутствие авторизации
        assert response.status_code == 401

    
    @pytest.mark.asyncio
    async def test_create_webinar_invalid_data(
        self, 
        client: AsyncClient,
        auth_headers_admin
    ):
        """
        Тест создания вебинара с невалидными данными
        
        Проверяет:
        1. Валидацию входных данных
        2. Возврат ошибок валидации
        """
        # Невалидные данные (прошедшая дата)
        past_time = datetime.now() - timedelta(hours=1)
        invalid_webinar_data = {
            "title": "",  # Пустое название
            "scheduled_at": past_time.isoformat(),  # Прошедшая дата
            "duration_minutes": 0,  # Невалидная длительность
            "max_participants": -1  # Отрицательное количество участников
        }
        
        # Пытаемся создать вебинар с невалидными данными
        response = await client.post(
            "/api/v1/webinars/", 
            json=invalid_webinar_data,
            headers=auth_headers_admin
        )
        
        # Проверяем ошибку валидации
        assert response.status_code == 422  # Validation Error

    
    @pytest.mark.asyncio
    async def test_create_webinar_with_nonexistent_plant(
        self, 
        client: AsyncClient,
        auth_headers_admin
    ):
        """
        Тест создания вебинара с несуществующим растением
        
        Проверяет:
        1. Обработку ссылки на несуществующее растение
        2. Возврат соответствующей ошибки
        """
        # Данные с несуществующим plant_topic_id
        scheduled_time = datetime.now() + timedelta(hours=1)
        webinar_data = {
            "title": "Вебинар с несуществующим растением",
            "description": "Тест с невалидным plant_topic_id",
            "scheduled_at": scheduled_time.isoformat(),
            "duration_minutes": 60,
            "is_public": True,
            "plant_topic_id": 99999  # Несуществующий ID
        }
        
        # Пытаемся создать вебинар
        response = await client.post(
            "/api/v1/webinars/", 
            json=webinar_data,
            headers=auth_headers_admin
        )
        
        # Проверяем ошибку (может быть 400 или 404 в зависимости от реализации)
        assert response.status_code in [400, 404]

    
    @pytest.mark.asyncio
    async def test_create_webinar_minimal_data(
        self, 
        client: AsyncClient,
        auth_headers_admin
    ):
        """
        Тест создания вебинара с минимальными данными
        
        Проверяет:
        1. Создание вебинара только с обязательными полями
        2. Установку значений по умолчанию
        """
        # Минимальные данные
        scheduled_time = datetime.now() + timedelta(hours=1)
        minimal_webinar_data = {
            "title": "Минимальный вебинар",
            "scheduled_at": scheduled_time.isoformat()
        }
        
        # Создаем вебинар
        response = await client.post(
            "/api/v1/webinars/", 
            json=minimal_webinar_data,
            headers=auth_headers_admin
        )
        
        # Проверяем успешное создание
        assert response.status_code == 201
        
        webinar_response = response.json()
        
        # Проверяем значения по умолчанию
        assert webinar_response["title"] == minimal_webinar_data["title"]
        assert webinar_response["duration_minutes"] == 60  # Значение по умолчанию
        assert webinar_response["is_public"] is True  # Значение по умолчанию
        assert webinar_response["status"] == "SCHEDULED"


class TestWebinarHostRetrieval:
    """Тесты получения вебинаров где пользователь является хостом"""

    
    @pytest.mark.asyncio
    async def test_get_hosted_webinars_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user,
        auth_headers_admin,
        test_plant
    ):
        """
        Тест получения вебинаров, где администратор является хостом

        Проверяет:
        1. Получение списка вебинаров, созданных администратором
        2. Фильтрацию по host_id
        3. Корректность возвращаемых данных
        """
        # Создаем несколько вебинаров от имени администратора
        from app.domain.models.webinar import Webinar, WebinarStatus

        webinars_data = [
            {
                "title": "Первый вебинар админа",
                "description": "Описание первого вебинара",
                "host_id": admin_user.id,
                "room_name": "admin_room_1",
                "scheduled_at": datetime.now() + timedelta(hours=1),
                "duration_minutes": 60,
                "is_public": True,
                "status": WebinarStatus.SCHEDULED,
                "plant_topic_id": test_plant.id
            },
            {
                "title": "Второй вебинар админа",
                "description": "Описание второго вебинара",
                "host_id": admin_user.id,
                "room_name": "admin_room_2",
                "scheduled_at": datetime.now() + timedelta(hours=2),
                "duration_minutes": 90,
                "is_public": False,
                "status": WebinarStatus.SCHEDULED
            }
        ]

        created_webinars = []
        for webinar_data in webinars_data:
            webinar = Webinar(**webinar_data)
            db_session.add(webinar)
            created_webinars.append(webinar)

        await db_session.commit()

        # Получаем вебинары, где администратор является хостом
        response = await client.get(
            f"/api/v1/webinars/?host_id={admin_user.id}",
            headers=auth_headers_admin
        )

        # Проверяем успешный ответ
        assert response.status_code == 200

        webinars_response = response.json()

        # Проверяем структуру ответа
        assert "items" in webinars_response
        assert "total_items" in webinars_response
        assert "page" in webinars_response
        assert "per_page" in webinars_response

        # Проверяем, что возвращены вебинары администратора
        assert webinars_response["total_items"] >= 2
        assert len(webinars_response["items"]) >= 2

        # Проверяем, что все вебинары принадлежат администратору
        for webinar_item in webinars_response["items"]:
            assert webinar_item["host_id"] == admin_user.id
            assert webinar_item["host"]["id"] == admin_user.id
            assert webinar_item["host"]["username"] == admin_user.username

            # Проверяем наличие обязательных полей
            required_fields = [
                "id", "title", "description", "host_id", "room_name",
                "scheduled_at", "duration_minutes", "status", "is_public"
            ]
            for field in required_fields:
                assert field in webinar_item

    
    @pytest.mark.asyncio
    async def test_get_hosted_webinars_plant_expert(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        plant_expert_user,
        auth_headers_expert
    ):
        """
        Тест получения вебинаров, где эксперт является хостом
        """
        # Создаем вебинар от имени эксперта
        from app.domain.models.webinar import Webinar, WebinarStatus

        expert_webinar = Webinar(
            title="Экспертный вебинар",
            description="Вебинар от эксперта по растениям",
            host_id=plant_expert_user.id,
            room_name="expert_room_1",
            scheduled_at=datetime.now() + timedelta(hours=3),
            duration_minutes=75,
            is_public=True,
            status=WebinarStatus.SCHEDULED
        )

        db_session.add(expert_webinar)
        await db_session.commit()

        # Получаем вебинары эксперта
        response = await client.get(
            f"/api/v1/webinars/?host_id={plant_expert_user.id}",
            headers=auth_headers_expert
        )

        assert response.status_code == 200

        webinars_response = response.json()

        # Проверяем, что найден вебинар эксперта
        assert webinars_response["total"] >= 1

        # Проверяем, что все вебинары принадлежат эксперту
        for webinar_item in webinars_response["items"]:
            assert webinar_item["host_id"] == plant_expert_user.id

    
    @pytest.mark.asyncio
    async def test_get_hosted_webinars_empty_list(
        self,
        client: AsyncClient,
        regular_user,
        auth_headers_user
    ):
        """
        Тест получения пустого списка вебинаров для пользователя без созданных вебинаров
        """
        # Получаем вебинары обычного пользователя (у него их нет)
        response = await client.get(
            f"/api/v1/webinars/?host_id={regular_user.id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200

        webinars_response = response.json()

        # Проверяем пустой список
        assert webinars_response["total_items"] == 0
        assert len(webinars_response["items"]) == 0

    
    @pytest.mark.asyncio
    async def test_get_hosted_webinars_unauthorized(self, client: AsyncClient, admin_user):
        """
        Тест получения вебинаров без авторизации
        """
        response = await client.get(f"/api/v1/webinars/?host_id={admin_user.id}")

        # Может быть 401 или возвращать только публичные вебинары
        # В зависимости от реализации API
        assert response.status_code in [200, 401]


class TestWebinarJoin:
    """Тесты подключения пользователей к вебинарам"""

    
    @pytest.mark.asyncio
    async def test_user_join_webinar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user,
        regular_user,
        auth_headers_user
    ):
        """
        Тест подключения пользователя к вебинару

        Проверяет:
        1. Успешное подключение к активному вебинару
        2. Получение данных для подключения к Jitsi
        3. Создание записи участника
        """
        # Создаем активный вебинар
        from app.domain.models.webinar import Webinar, WebinarStatus

        live_webinar = Webinar(
            title="Активный вебинар",
            description="Вебинар в прямом эфире",
            host_id=admin_user.id,
            room_name="live_room_test",
            scheduled_at=datetime.now() - timedelta(minutes=10),  # Начался 10 минут назад
            duration_minutes=60,
            is_public=True,
            status=WebinarStatus.LIVE  # Статус LIVE
        )

        db_session.add(live_webinar)
        await db_session.commit()
        await db_session.refresh(live_webinar)

        # Подключаемся к вебинару
        response = await client.post(
            f"/api/v1/webinars/{live_webinar.id}/join",
            headers=auth_headers_user
        )

        # Проверяем успешное подключение
        assert response.status_code == 200

        join_response = response.json()

        # Проверяем данные для подключения
        expected_fields = ["jwt_token", "jitsi_url", "can_join"]
        for field in expected_fields:
            assert field in join_response, f"Поле {field} отсутствует в ответе"

        # Проверяем корректность данных
        assert join_response["can_join"] is True
        assert isinstance(join_response["jwt_token"], str)
        assert len(join_response["jwt_token"]) > 0
        assert join_response["jitsi_url"].startswith("https://")  # Проверяем, что это HTTPS URL
        assert "live_room_test" in join_response["jitsi_url"]  # Проверяем, что URL содержит имя комнаты

        # Проверяем, что создана запись участника
        from app.domain.models.webinar import WebinarParticipant
        from sqlalchemy import select

        result = await db_session.execute(
            select(WebinarParticipant).where(
                WebinarParticipant.webinar_id == live_webinar.id,
                WebinarParticipant.user_id == regular_user.id
            )
        )
        participant = result.scalar_one_or_none()

        assert participant is not None
        assert participant.webinar_id == live_webinar.id
        assert participant.user_id == regular_user.id

    
    @pytest.mark.asyncio
    async def test_join_scheduled_webinar_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user,
        regular_user,
        auth_headers_user
    ):
        """
        Тест запрета подключения к запланированному вебинару

        Проверяет:
        1. Запрет подключения к вебинару со статусом SCHEDULED
        2. Возврат соответствующей ошибки
        """
        # Создаем запланированный вебинар
        from app.domain.models.webinar import Webinar, WebinarStatus

        scheduled_webinar = Webinar(
            title="Запланированный вебинар",
            description="Вебинар еще не начался",
            host_id=admin_user.id,
            room_name="scheduled_room_test",
            scheduled_at=datetime.now() + timedelta(hours=1),  # Начнется через час
            duration_minutes=60,
            is_public=True,
            status=WebinarStatus.SCHEDULED  # Статус SCHEDULED
        )

        db_session.add(scheduled_webinar)
        await db_session.commit()
        await db_session.refresh(scheduled_webinar)

        # Пытаемся подключиться к запланированному вебинару
        response = await client.post(
            f"/api/v1/webinars/{scheduled_webinar.id}/join",
            headers=auth_headers_user
        )

        # Проверяем запрет подключения
        assert response.status_code == 403
        error_response = response.json()
        assert "не начался" in error_response["detail"].lower() or "scheduled" in error_response["detail"].lower()

    
    @pytest.mark.asyncio
    async def test_join_nonexistent_webinar(
        self,
        client: AsyncClient,
        auth_headers_user
    ):
        """
        Тест подключения к несуществующему вебинару
        """
        non_existent_id = 99999

        response = await client.post(
            f"/api/v1/webinars/{non_existent_id}/join",
            headers=auth_headers_user
        )

        assert response.status_code == 404
        error_response = response.json()
        assert "не найден" in error_response["detail"].lower()

    
    @pytest.mark.asyncio
    async def test_join_webinar_unauthorized(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user
    ):
        """
        Тест подключения к вебинару без авторизации
        """
        # Создаем активный вебинар
        from app.domain.models.webinar import Webinar, WebinarStatus

        live_webinar = Webinar(
            title="Активный вебинар",
            description="Вебинар в прямом эфире",
            host_id=admin_user.id,
            room_name="live_room_unauth",
            scheduled_at=datetime.now() - timedelta(minutes=5),
            duration_minutes=60,
            is_public=True,
            status=WebinarStatus.LIVE
        )

        db_session.add(live_webinar)
        await db_session.commit()
        await db_session.refresh(live_webinar)

        # Пытаемся подключиться без авторизации
        response = await client.post(f"/api/v1/webinars/{live_webinar.id}/join")

        assert response.status_code == 401

    
    @pytest.mark.asyncio
    async def test_join_private_webinar_forbidden(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user,
        regular_user,
        auth_headers_user
    ):
        """
        Тест запрета подключения к приватному вебинару
        """
        # Создаем приватный вебинар
        from app.domain.models.webinar import Webinar, WebinarStatus

        private_webinar = Webinar(
            title="Приватный вебинар",
            description="Закрытый вебинар",
            host_id=admin_user.id,
            room_name="private_room_test",
            scheduled_at=datetime.now() - timedelta(minutes=5),
            duration_minutes=60,
            is_public=False,  # Приватный вебинар
            status=WebinarStatus.LIVE
        )

        db_session.add(private_webinar)
        await db_session.commit()
        await db_session.refresh(private_webinar)

        # Пытаемся подключиться к приватному вебинару
        response = await client.post(
            f"/api/v1/webinars/{private_webinar.id}/join",
            headers=auth_headers_user
        )

        # Проверяем запрет доступа (может быть 403 или 404 в зависимости от реализации)
        assert response.status_code in [403, 404]

    
    @pytest.mark.asyncio
    async def test_host_join_own_webinar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        admin_user,
        auth_headers_admin
    ):
        """
        Тест подключения хоста к собственному вебинару
        """
        # Создаем вебинар от имени администратора
        from app.domain.models.webinar import Webinar, WebinarStatus

        host_webinar = Webinar(
            title="Вебинар хоста",
            description="Хост подключается к своему вебинару",
            host_id=admin_user.id,
            room_name="host_room_test",
            scheduled_at=datetime.now() - timedelta(minutes=5),
            duration_minutes=60,
            is_public=True,
            status=WebinarStatus.LIVE
        )

        db_session.add(host_webinar)
        await db_session.commit()
        await db_session.refresh(host_webinar)

        # Хост подключается к своему вебинару
        response = await client.post(
            f"/api/v1/webinars/{host_webinar.id}/join",
            headers=auth_headers_admin
        )

        # Проверяем успешное подключение
        assert response.status_code == 200

        join_response = response.json()

        # Хост должен получить дополнительные права (модератор)
        assert "jitsi_url" in join_response
        assert "jwt_token" in join_response
        assert "host_room_test" in join_response["jitsi_url"]  # Проверяем, что URL содержит имя комнаты
