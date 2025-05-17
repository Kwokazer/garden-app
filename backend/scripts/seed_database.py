#!/usr/bin/env python3
import asyncio
import os
import sys
import datetime
import random

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, text

from app.domain.models.plant import Plant, PlantType
from app.domain.models.plant_category import PlantCategory, PlantToCategory
from app.domain.models.climate_zone import ClimateZone, PlantToClimateZone
from app.domain.models.plant_image import PlantImage
from app.domain.models.question import Question
from app.domain.models.answer import Answer
from app.domain.models.user import User
from app.infrastructure.database.connection import AsyncSessionLocal

# Тестовые данные для категорий растений
CATEGORIES = [
    {"name": "Деревья", "description": "Высокие древесные растения с одним стволом"},
    {"name": "Кустарники", "description": "Многоствольные древесные растения"},
    {"name": "Цветы", "description": "Растения с декоративными цветками"},
    {"name": "Овощи", "description": "Съедобные растения, выращиваемые для кулинарии"},
    {"name": "Фрукты", "description": "Растения, дающие съедобные плоды"},
    {"name": "Травы", "description": "Растения, используемые как приправы и лекарства"},
    {"name": "Суккуленты", "description": "Растения, способные запасать воду"},
    {"name": "Лианы", "description": "Вьющиеся и цепляющиеся растения"},
    {"name": "Водные растения", "description": "Растения, растущие в воде или вблизи нее"},
    {"name": "Папоротники", "description": "Нецветущие сосудистые растения"},
]

# Тестовые данные для климатических зон
CLIMATE_ZONES = [
    {"name": "Тропическая", "zone_number": 1, "temperature_range": "выше 18°C", "description": "Жаркий климат без морозов"},
    {"name": "Субтропическая", "zone_number": 2, "temperature_range": "15-18°C", "description": "Мягкие зимы, редкие морозы"},
    {"name": "Умеренная", "zone_number": 3, "temperature_range": "10-15°C", "description": "Выраженные сезоны, умеренные морозы"},
    {"name": "Континентальная", "zone_number": 4, "temperature_range": "5-10°C", "description": "Жаркое лето и холодная зима"},
    {"name": "Субарктическая", "zone_number": 5, "temperature_range": "0-5°C", "description": "Короткое лето, длинная зима"},
    {"name": "Арктическая", "zone_number": 6, "temperature_range": "ниже 0°C", "description": "Экстремально холодный климат"},
]

# Тестовые данные для растений
PLANTS = [
    {
        "name": "Клен остролистный",
        "scientific_name": "Acer platanoides",
        "description": "Листопадное дерево с широкой кроной и красивыми листьями",
        "growth_height_min": 200,
        "growth_height_max": 3000,
        "growth_rate": "средний",
        "plant_type": PlantType.TREE,
        "popularity_score": 85,
        "bloom_season": "весна",
        "bloom_color": "зеленовато-желтый",
        "hardiness_zone_min": 3,
        "hardiness_zone_max": 7,
        "care_instructions": "Требует умеренного полива. Предпочитает плодородные, хорошо дренированные почвы.",
        "planting_tips": "Сажайте в местах с полным солнцем или частичной тенью.",
        "pruning_tips": "Обрезайте ранней весной для формирования кроны.",
        "categories": [0],  # Деревья
        "climate_zones": [2, 3, 4],  # Умеренная, Континентальная и Субтропическая
        "images": [
            {"url": "https://images.unsplash.com/photo-1618994175617-35a7c0f15963", "description": "Клен остролистный осенью", "is_primary": True},
            {"url": "https://images.unsplash.com/photo-1533038590840-1f704a1f21b9", "description": "Листья клена крупным планом", "is_primary": False},
        ]
    },
    {
        "name": "Роза чайная",
        "scientific_name": "Rosa × odorata",
        "description": "Популярный садовый цветок с ароматными цветками",
        "growth_height_min": 60,
        "growth_height_max": 150,
        "growth_rate": "средний",
        "plant_type": PlantType.FLOWER,
        "popularity_score": 95,
        "bloom_season": "лето-осень",
        "bloom_color": "разные цвета",
        "hardiness_zone_min": 5,
        "hardiness_zone_max": 9,
        "care_instructions": "Нуждается в регулярном поливе и подкормке. Устойчива к жаре, но требует защиты от мороза.",
        "planting_tips": "Сажайте в солнечном месте с хорошей циркуляцией воздуха.",
        "pruning_tips": "Обрезайте ранней весной, удаляя старые и поврежденные побеги.",
        "categories": [2],  # Цветы
        "climate_zones": [1, 2, 3],  # Тропическая, Субтропическая, Умеренная
        "images": [
            {"url": "https://images.unsplash.com/photo-1469044155030-15ee92a47b8f", "description": "Розовая чайная роза", "is_primary": True},
            {"url": "https://images.unsplash.com/photo-1551269901-5c5e14c25df7", "description": "Бутон чайной розы", "is_primary": False},
        ]
    },
    {
        "name": "Алоэ вера",
        "scientific_name": "Aloe vera",
        "description": "Суккулентное растение с лечебными свойствами",
        "growth_height_min": 30,
        "growth_height_max": 100,
        "growth_rate": "медленный",
        "plant_type": PlantType.SUCCULENT,
        "popularity_score": 80,
        "bloom_season": "лето",
        "bloom_color": "оранжевый",
        "hardiness_zone_min": 8,
        "hardiness_zone_max": 11,
        "care_instructions": "Нуждается в минимальном поливе. Избегайте переувлажнения.",
        "planting_tips": "Используйте хорошо дренированную почву для суккулентов.",
        "pruning_tips": "Удаляйте поврежденные листья по мере необходимости.",
        "categories": [6],  # Суккуленты
        "climate_zones": [0, 1],  # Тропическая и Субтропическая
        "images": [
            {"url": "https://images.unsplash.com/photo-1596547609061-35847ffdbfd8", "description": "Алоэ вера в горшке", "is_primary": True},
            {"url": "https://images.unsplash.com/photo-1625600243103-1dc6824c6c7a", "description": "Лист алоэ вера с гелем", "is_primary": False},
        ]
    },
    {
        "name": "Томат",
        "scientific_name": "Solanum lycopersicum",
        "description": "Популярное овощное растение с съедобными плодами",
        "growth_height_min": 50,
        "growth_height_max": 200,
        "growth_rate": "быстрый",
        "plant_type": PlantType.VEGETABLE,
        "popularity_score": 90,
        "bloom_season": "лето",
        "bloom_color": "желтый",
        "hardiness_zone_min": 5,
        "hardiness_zone_max": 11,
        "care_instructions": "Регулярный полив и подкормка. Избегайте попадания воды на листья.",
        "planting_tips": "Сажайте в солнечном месте после заморозков.",
        "pruning_tips": "Удаляйте пасынки для увеличения урожая.",
        "categories": [3],  # Овощи
        "climate_zones": [2, 3],  # Умеренная и Континентальная
        "images": [
            {"url": "https://images.unsplash.com/photo-1592841200221-a6898f307baa", "description": "Спелые томаты на ветке", "is_primary": True},
            {"url": "https://images.unsplash.com/photo-1519181236443-b175d4c3ca1d", "description": "Цветы томата", "is_primary": False},
        ]
    },
    {
        "name": "Базилик",
        "scientific_name": "Ocimum basilicum",
        "description": "Ароматное травянистое растение, используемое в кулинарии",
        "growth_height_min": 20,
        "growth_height_max": 60,
        "growth_rate": "быстрый",
        "plant_type": PlantType.HERB,
        "popularity_score": 85,
        "bloom_season": "лето",
        "bloom_color": "белый",
        "hardiness_zone_min": 4,
        "hardiness_zone_max": 10,
        "care_instructions": "Регулярный полив, но избегайте переувлажнения. Любит солнце и тепло.",
        "planting_tips": "Сажайте после заморозков в богатую питательными веществами почву.",
        "pruning_tips": "Регулярно срезайте верхушки для стимуляции роста и предотвращения цветения.",
        "categories": [5],  # Травы
        "climate_zones": [1, 2, 3],  # Тропическая, Субтропическая, Умеренная
        "images": [
            {"url": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf", "description": "Куст базилика", "is_primary": True},
            {"url": "https://images.unsplash.com/photo-1598511726623-d2e9996e8f76", "description": "Листья базилика крупным планом", "is_primary": False},
        ]
    },
]

# Тестовые вопросы и ответы
QUESTIONS = [
    {
        "title": "Как часто поливать клен?",
        "body": "Недавно посадил клен в своем саду. Как часто его нужно поливать в первый год?",
        "plant_idx": 0,  # Индекс клена в массиве PLANTS
        "is_solved": False,
        "answers": [
            {
                "body": "В первый год после посадки клен нуждается в регулярном поливе, примерно 1-2 раза в неделю в зависимости от погоды. Почва должна быть влажной, но не переувлажненной. В жаркую погоду увеличьте частоту полива.",
                "is_accepted": True
            },
            {
                "body": "Я поливаю свой клен раз в неделю, и он прекрасно себя чувствует.",
                "is_accepted": False
            }
        ]
    },
    {
        "title": "Желтеют листья у розы",
        "body": "У моей чайной розы желтеют и опадают нижние листья. Что может быть причиной?",
        "plant_idx": 1,  # Индекс розы в массиве PLANTS
        "is_solved": True,
        "answers": [
            {
                "body": "Пожелтение нижних листьев розы может быть вызвано несколькими причинами: 1) Естественное старение листьев; 2) Недостаток или избыток влаги; 3) Недостаток питательных веществ, особенно азота; 4) Грибковые заболевания. Проверьте режим полива и подкормите розу комплексным удобрением.",
                "is_accepted": True
            }
        ]
    },
    {
        "title": "Когда лучше сажать томаты?",
        "body": "Какое оптимальное время для посадки томатов в открытый грунт?",
        "plant_idx": 3,  # Индекс томата в массиве PLANTS
        "is_solved": False,
        "answers": []
    }
]

async def get_db_session() -> AsyncSession:
    """Получить асинхронную сессию для работы с БД"""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def seed_database():
    """Функция для заполнения базы данных тестовыми данными"""
    async for session in get_db_session():
        # Проверка и получение пользователя для вопросов и ответов
        user_id = await get_or_create_test_user(session)
        
        # Создаем и сохраняем базовые данные
        categories = await create_categories(session)
        climate_zones = await create_climate_zones(session)
        plants = await create_plants(session, categories, climate_zones)
        
        # Дополнительные данные
        await create_questions_and_answers(session, plants, user_id)
        
        # Сохраняем все изменения
        await session.commit()
        print("База данных успешно заполнена тестовыми данными!")

async def get_or_create_test_user(session: AsyncSession) -> int:
    """Получить или создать тестового пользователя"""
    # Проверяем наличие пользователей
    query = select(User).limit(1)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if user:
        print(f"Использую существующего пользователя с ID {user.id}")
        return user.id
    
    # Если нет пользователей, создаем тестового
    print("Создаю тестового пользователя...")
    test_user = User(
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password = "password"
        is_active=True,
        is_verified=True,
        is_superuser=True,
        username="testuser",
        first_name="Test",
        last_name="User"
    )
    session.add(test_user)
    await session.flush()
    print(f"Создан тестовый пользователь с ID {test_user.id}")
    return test_user.id

async def create_categories(session: AsyncSession) -> dict[str, int]:
    """Создание категорий растений"""
    print("Создание категорий растений...")
    categories = {}
    
    for category_data in CATEGORIES:
        # Проверяем, существует ли категория
        category_name = category_data["name"]
        query = select(PlantCategory).filter(PlantCategory.name == category_name)
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            categories[category_name] = existing.id
        else:
            category = PlantCategory(**category_data)
            session.add(category)
            await session.flush()
            categories[category_name] = category.id
    
    await session.flush()
    print(f"Создано или получено {len(categories)} категорий")
    return categories

async def create_climate_zones(session: AsyncSession) -> dict[str, int]:
    """Создание климатических зон"""
    print("Создание климатических зон...")
    climate_zones = {}
    
    for zone_data in CLIMATE_ZONES:
        # Проверяем, существует ли зона
        zone_name = zone_data["name"]
        query = select(ClimateZone).filter(ClimateZone.name == zone_name)
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            climate_zones[zone_name] = existing.id
        else:
            zone = ClimateZone(**zone_data)
            session.add(zone)
            await session.flush()
            climate_zones[zone_name] = zone.id
    
    await session.flush()
    print(f"Создано или получено {len(climate_zones)} климатических зон")
    return climate_zones

async def create_plants(
    session: AsyncSession, 
    categories: dict[str, int], 
    climate_zones: dict[str, int]
) -> list[Plant]:
    """Создание растений с их связями"""
    print("Создание растений...")
    plants = []
    
    for plant_data in PLANTS:
        # Копируем данные, чтобы не изменять оригинал
        data = plant_data.copy()
        
        # Извлекаем данные о связях
        category_indices = data.pop("categories", [])
        zone_indices = data.pop("climate_zones", [])
        image_data = data.pop("images", [])
        
        # Проверяем, существует ли растение
        plant_name = data["name"]
        query = select(Plant).filter(Plant.name == plant_name)
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            plants.append(existing)
            continue
        
        # Создаем растение
        plant = Plant(**data)
        session.add(plant)
        await session.flush()
        
        # Добавляем связи с категориями
        for idx in category_indices:
            category_name = CATEGORIES[idx]["name"]
            category_id = categories.get(category_name)
            if category_id:
                link = PlantToCategory(plant_id=plant.id, category_id=category_id)
                session.add(link)
        
        # Добавляем связи с климатическими зонами
        for idx in zone_indices:
            zone_name = CLIMATE_ZONES[idx]["name"]
            zone_id = climate_zones.get(zone_name)
            if zone_id:
                link = PlantToClimateZone(plant_id=plant.id, climate_zone_id=zone_id)
                session.add(link)
        
        # Добавляем изображения
        for img in image_data:
            image = PlantImage(plant_id=plant.id, **img)
            session.add(image)
        
        plants.append(plant)
    
    await session.flush()
    print(f"Создано или получено {len(plants)} растений")
    return plants

async def create_questions_and_answers(
    session: AsyncSession, 
    plants: list[Plant], 
    user_id: int
):
    """Создание вопросов и ответов"""
    print("Создание вопросов и ответов...")
    questions_count = 0
    answers_count = 0
    
    # Создаем основные вопросы из тестовых данных
    for question_data in QUESTIONS:
        # Копируем данные
        data = question_data.copy()
        
        # Получаем связанное растение и ответы
        plant_idx = data.pop("plant_idx")
        answers_data = data.pop("answers", [])
        
        if plant_idx >= len(plants):
            continue
            
        plant = plants[plant_idx]
        
        # Проверяем, существует ли вопрос
        title = data["title"]
        query = select(Question).filter(Question.title == title, Question.plant_id == plant.id)
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            continue
        
        # Создаем вопрос
        question = Question(
            plant_id=plant.id, 
            author_id=user_id,
            **data
        )
        session.add(question)
        await session.flush()
        questions_count += 1
        
        # Создаем ответы
        for answer_data in answers_data:
            answer = Answer(
                question_id=question.id,
                author_id=user_id,
                **answer_data
            )
            session.add(answer)
            answers_count += 1
    
    # Добавим еще несколько случайных вопросов для разнообразия
    for _ in range(5):
        plant = random.choice(plants)
        question_titles = [
            f"Проблема с {plant.name}",
            f"Как ухаживать за {plant.name}?",
            f"Совместимость {plant.name} с другими растениями",
            f"Размножение {plant.name}",
            f"Болезни {plant.name}"
        ]
        title = random.choice(question_titles)
        
        # Проверяем, существует ли такой вопрос
        query = select(Question).filter(Question.title == title, Question.plant_id == plant.id)
        result = await session.execute(query)
        existing = result.scalars().first()
        
        if existing:
            continue
        
        question = Question(
            title=title,
            body=f"У меня есть вопрос по {plant.name}. {random.choice(['Как правильно ухаживать?', 'Когда лучше сажать?', 'Можно ли выращивать в контейнере?'])}",
            plant_id=plant.id,
            author_id=user_id,
            is_solved=random.choice([True, False])
        )
        session.add(question)
        await session.flush()
        questions_count += 1
        
        # Добавляем от 0 до 2 ответов
        for _ in range(random.randint(0, 2)):
            answer = Answer(
                body=f"Ответ на вопрос о {plant.name}. {random.choice(['Рекомендую...', 'В моем опыте...', 'Специалисты советуют...'])}",
                question_id=question.id,
                author_id=user_id,
                is_accepted=random.choice([True, False])
            )
            session.add(answer)
            answers_count += 1
    
    await session.flush()
    print(f"Создано {questions_count} вопросов и {answers_count} ответов")

if __name__ == "__main__":
    asyncio.run(seed_database()) 