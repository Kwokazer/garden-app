"""
Тесты для работы с растениями
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestPlantRetrieval:
    """Тесты получения информации о растениях"""

    @pytest.mark.asyncio
    async def test_get_plant_information(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession,
        test_plant
    ):
        """
        Тест получения информации о растении
        
        Проверяет:
        1. Получение детальной информации о растении по ID
        2. Корректность возвращаемых данных
        3. Структуру ответа
        """
        plant_id = test_plant.id
        
        # Получаем информацию о растении
        response = await client.get(f"/api/v1/plants/{plant_id}")
        
        # Проверяем успешный ответ
        assert response.status_code == 200
        
        plant_data = response.json()
        
        # Проверяем основные поля
        assert plant_data["id"] == plant_id
        assert plant_data["name"] == test_plant.name
        assert plant_data["latin_name"] == test_plant.latin_name
        assert plant_data["description"] == test_plant.description
        assert plant_data["plant_type"] == test_plant.plant_type.value
        assert plant_data["popularity_score"] == test_plant.popularity_score
        
        # Проверяем наличие обязательных полей в ответе
        required_fields = [
            "id", "name", "latin_name", "description", 
            "plant_type", "popularity_score", "created_at", "updated_at"
        ]
        for field in required_fields:
            assert field in plant_data, f"Поле {field} отсутствует в ответе"
        
        # Проверяем типы данных
        assert isinstance(plant_data["id"], int)
        assert isinstance(plant_data["name"], str)
        assert isinstance(plant_data["popularity_score"], int)
        assert isinstance(plant_data["created_at"], str)
        assert isinstance(plant_data["updated_at"], str)

    @pytest.mark.asyncio
    async def test_get_plant_not_found(self, client: AsyncClient):
        """Тест получения несуществующего растения"""
        non_existent_id = 99999
        
        response = await client.get(f"/api/v1/plants/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "не найден" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_plants_list(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """
        Тест получения списка растений с пагинацией
        
        Проверяет:
        1. Получение списка растений
        2. Пагинацию
        3. Структуру ответа со списком
        """
        # Создаем несколько тестовых растений
        from app.domain.models.plant import Plant, PlantType
        
        plants_data = [
            {
                "name": "Фикус Бенджамина",
                "latin_name": "Ficus benjamina",
                "description": "Популярное комнатное растение",
                "plant_type": PlantType.TREE,
                "popularity_score": 85
            },
            {
                "name": "Роза садовая",
                "latin_name": "Rosa gallica",
                "description": "Красивое садовое растение",
                "plant_type": PlantType.FLOWER,
                "popularity_score": 95
            },
            {
                "name": "Лаванда",
                "latin_name": "Lavandula angustifolia",
                "description": "Ароматное растение",
                "plant_type": PlantType.HERB,
                "popularity_score": 75
            }
        ]
        
        created_plants = []
        for plant_data in plants_data:
            plant = Plant(**plant_data)
            db_session.add(plant)
            created_plants.append(plant)
        
        await db_session.commit()
        
        # Получаем список растений
        response = await client.get("/api/v1/plants/")
        
        assert response.status_code == 200
        
        plants_response = response.json()
        
        # Проверяем структуру ответа
        assert "items" in plants_response
        assert "total" in plants_response
        assert "page" in plants_response
        assert "per_page" in plants_response
        assert "pages" in plants_response
        
        # Проверяем, что растения возвращаются
        assert len(plants_response["items"]) >= 3
        assert plants_response["total"] >= 3
        
        # Проверяем структуру элементов списка
        for plant_item in plants_response["items"]:
            assert "id" in plant_item
            assert "name" in plant_item
            assert "latin_name" in plant_item
            assert "plant_type" in plant_item

    @pytest.mark.asyncio
    async def test_get_plants_with_filters(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """Тест получения растений с фильтрацией"""
        # Создаем растения разных типов
        from app.domain.models.plant import Plant, PlantType
        
        indoor_plant = Plant(
            name="Комнатная пальма",
            latin_name="Chamaedorea elegans",
            description="Красивая комнатная пальма",
            plant_type=PlantType.TREE,
            popularity_score=80
        )

        outdoor_plant = Plant(
            name="Садовая ромашка",
            latin_name="Bellis perennis",
            description="Простая садовая ромашка",
            plant_type=PlantType.FLOWER,
            popularity_score=60
        )
        
        db_session.add(indoor_plant)
        db_session.add(outdoor_plant)
        await db_session.commit()
        
        # Фильтруем только деревья
        response = await client.get("/api/v1/plants/?plant_type=TREE")

        assert response.status_code == 200

        plants_response = response.json()

        # Проверяем, что все возвращенные растения - деревья
        for plant_item in plants_response["items"]:
            assert plant_item["plant_type"] == "TREE"

    @pytest.mark.asyncio
    async def test_get_plants_with_search(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """Тест поиска растений по названию"""
        # Создаем растение с уникальным названием
        from app.domain.models.plant import Plant, PlantType
        
        searchable_plant = Plant(
            name="Уникальное тестовое растение",
            latin_name="Uniquus testus",
            description="Растение для тестирования поиска",
            plant_type=PlantType.SUCCULENT,
            popularity_score=50
        )
        
        db_session.add(searchable_plant)
        await db_session.commit()
        
        # Ищем по части названия
        response = await client.get("/api/v1/plants/?name=Уникальное")
        
        assert response.status_code == 200
        
        plants_response = response.json()
        
        # Проверяем, что найдено растение
        assert plants_response["total"] >= 1
        
        # Проверяем, что найденное растение содержит искомое слово
        found = False
        for plant_item in plants_response["items"]:
            if "Уникальное" in plant_item["name"]:
                found = True
                break
        
        assert found, "Растение с искомым названием не найдено"

    @pytest.mark.asyncio
    async def test_get_plants_pagination(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """Тест пагинации списка растений"""
        # Создаем много растений для тестирования пагинации
        from app.domain.models.plant import Plant, PlantType
        
        plants = []
        for i in range(25):  # Создаем 25 растений
            plant = Plant(
                name=f"Растение {i+1}",
                latin_name=f"Plantus {i+1}",
                description=f"Описание растения {i+1}",
                plant_type=PlantType.HERB,
                popularity_score=i * 2
            )
            plants.append(plant)
            db_session.add(plant)
        
        await db_session.commit()
        
        # Тестируем первую страницу
        response = await client.get("/api/v1/plants/?page=1&per_page=10")
        
        assert response.status_code == 200
        
        plants_response = response.json()
        
        # Проверяем пагинацию
        assert plants_response["page"] == 1
        assert plants_response["per_page"] == 10
        assert len(plants_response["items"]) == 10
        assert plants_response["total"] >= 25
        assert plants_response["pages"] >= 3
        
        # Тестируем вторую страницу
        response2 = await client.get("/api/v1/plants/?page=2&per_page=10")
        
        assert response2.status_code == 200
        
        plants_response2 = response2.json()
        
        assert plants_response2["page"] == 2
        assert len(plants_response2["items"]) == 10
        
        # Проверяем, что элементы на разных страницах разные
        page1_ids = {item["id"] for item in plants_response["items"]}
        page2_ids = {item["id"] for item in plants_response2["items"]}
        
        assert page1_ids.isdisjoint(page2_ids), "Элементы на разных страницах не должны пересекаться"
