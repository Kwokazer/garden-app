#!/usr/bin/env python3
# backend/scripts/seed_database.py

import asyncio
import json
import random
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Импорт моделей
from app.domain.models.base import Base, TimestampedModel, BaseModel
from app.domain.models.user import User, PrivacyLevel, UserRole
from app.domain.models.role import Role
from app.domain.models.permission import Permission
from app.domain.models.oauth_account import OAuthAccount
from app.domain.models.plant import (
    Plant, PlantType, LifeCycle, WateringFrequency, 
    LightLevel, HumidityLevel, CareDifficulty,
    FertilizingFrequency, RepottingFrequency, GrowthRate
)
from app.domain.models.plant_category import PlantCategory, PlantToCategory
from app.domain.models.climate_zone import ClimateZone, PlantToClimateZone
from app.domain.models.plant_image import PlantImage
from app.domain.models.tag import Tag, plant_tag
from app.domain.models.question import Question
from app.domain.models.answer import Answer
from app.domain.models.vote import QuestionVote, AnswerVote, VoteType

# Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Конфигурация базы данных
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/garden")

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Список разрешений
PERMISSIONS = [
    {"name": "users:read", "description": "Просмотр списка пользователей"},
    {"name": "users:write", "description": "Создание и редактирование пользователей"},
    {"name": "users:delete", "description": "Удаление пользователей"},
    {"name": "plants:read", "description": "Просмотр растений"},
    {"name": "plants:write", "description": "Создание и редактирование растений"},
    {"name": "plants:delete", "description": "Удаление растений"},
    {"name": "questions:read", "description": "Просмотр вопросов"},
    {"name": "questions:write", "description": "Создание и редактирование вопросов"},
    {"name": "questions:delete", "description": "Удаление вопросов"},
    {"name": "answers:read", "description": "Просмотр ответов"},
    {"name": "answers:write", "description": "Создание и редактирование ответов"},
    {"name": "answers:delete", "description": "Удаление ответов"},
    {"name": "categories:read", "description": "Просмотр категорий растений"},
    {"name": "categories:write", "description": "Создание и редактирование категорий"},
    {"name": "categories:delete", "description": "Удаление категорий"},
    {"name": "climate_zones:read", "description": "Просмотр климатических зон"},
    {"name": "climate_zones:write", "description": "Создание и редактирование климатических зон"},
    {"name": "climate_zones:delete", "description": "Удаление климатических зон"},
    {"name": "tags:read", "description": "Просмотр тегов"},
    {"name": "tags:write", "description": "Создание и редактирование тегов"},
    {"name": "tags:delete", "description": "Удаление тегов"},
]

# Список ролей и связанные с ними разрешения
ROLES = [
    {
        "name": "admin",
        "description": "Администратор системы",
        "permissions": [perm["name"] for perm in PERMISSIONS]
    },
    {
        "name": "moderator",
        "description": "Модератор контента",
        "permissions": [
            "plants:read", "plants:write", 
            "questions:read", "questions:write", "questions:delete", 
            "answers:read", "answers:write", "answers:delete",
            "categories:read", "tags:read", "climate_zones:read"
        ]
    },
    {
        "name": "plant_expert",
        "description": "Эксперт по растениям",
        "permissions": [
            "plants:read", "plants:write", 
            "questions:read", "answers:read", "answers:write",
            "categories:read", "tags:read", "climate_zones:read"
        ]
    },
    {
        "name": "user",
        "description": "Обычный пользователь",
        "permissions": [
            "plants:read", "questions:read", "questions:write", 
            "answers:read", "answers:write",
            "categories:read", "tags:read", "climate_zones:read"
        ]
    },
]

# Тестовые пользователи
USERS = [
    {
        "email": "admin@example.com",
        "username": "admin",
        "password": "Admin123!",
        "first_name": "Админ",
        "last_name": "Системы",
        "is_active": True,
        "is_verified": True,
        "privacy_level": PrivacyLevel.PUBLIC,
        "avatar_url": "https://i.pravatar.cc/150?u=admin",
        "roles": ["admin"]
    },
    {
        "email": "moderator@example.com",
        "username": "moderator",
        "password": "Moderator123!",
        "first_name": "Модератор",
        "last_name": "Контента",
        "is_active": True,
        "is_verified": True,
        "privacy_level": PrivacyLevel.LIMITED,
        "avatar_url": "https://i.pravatar.cc/150?u=moderator",
        "roles": ["moderator"]
    },
    {
        "email": "expert@example.com",
        "username": "plant_expert",
        "password": "Expert123!",
        "first_name": "Эксперт",
        "last_name": "Растений",
        "is_active": True,
        "is_verified": True,
        "privacy_level": PrivacyLevel.PUBLIC,
        "avatar_url": "https://i.pravatar.cc/150?u=expert",
        "roles": ["plant_expert"]
    }
]

# Добавим еще 10 обычных пользователей
for i in range(1, 11):
    USERS.append({
        "email": f"user{i}@example.com",
        "username": f"user{i}",
        "password": f"User{i}123!",
        "first_name": f"Пользователь {i}",
        "last_name": f"Фамилия {i}",
        "is_active": True,
        "is_verified": i > 2,  # первые 2 не верифицированы
        "privacy_level": random.choice(list(PrivacyLevel)),
        "avatar_url": f"https://i.pravatar.cc/150?u=user{i}",
        "roles": ["user"]
    })

# Категории растений с иерархической структурой
PLANT_CATEGORIES = [
    {"name": "Комнатные растения", "description": "Растения для выращивания в помещении", "parent_id": None},
    {"name": "Садовые растения", "description": "Растения для выращивания в саду", "parent_id": None},
    {"name": "Огородные растения", "description": "Овощи, фрукты и травы для огорода", "parent_id": None},
    
    {"name": "Цветущие комнатные", "description": "Комнатные растения с красивыми цветами", "parent_id": 1},
    {"name": "Декоративно-лиственные", "description": "Комнатные растения с красивыми листьями", "parent_id": 1},
    {"name": "Суккуленты и кактусы", "description": "Засухоустойчивые комнатные растения", "parent_id": 1},
    {"name": "Пальмы", "description": "Различные виды пальм для дома", "parent_id": 1},
    {"name": "Папоротники", "description": "Комнатные папоротники", "parent_id": 1},
    
    {"name": "Декоративные кустарники", "description": "Декоративные кустарники для сада", "parent_id": 2},
    {"name": "Деревья", "description": "Декоративные и плодовые деревья", "parent_id": 2},
    {"name": "Розы", "description": "Различные сорта роз", "parent_id": 2},
    {"name": "Многолетние цветы", "description": "Многолетние цветущие растения", "parent_id": 2},
    {"name": "Однолетние цветы", "description": "Однолетние цветущие растения", "parent_id": 2},
    {"name": "Луковичные", "description": "Растения с луковицами", "parent_id": 2},
    
    {"name": "Овощи", "description": "Овощные культуры", "parent_id": 3},
    {"name": "Фрукты и ягоды", "description": "Плодовые культуры", "parent_id": 3},
    {"name": "Зелень и пряные травы", "description": "Пряно-ароматические растения", "parent_id": 3},
]

# Теги для растений
TAGS = [
    {"name": "Неприхотливые", "description": "Растения, не требующие особого ухода"},
    {"name": "Теневыносливые", "description": "Растения, хорошо растущие в тени"},
    {"name": "Солнцелюбивые", "description": "Растения, требующие много света"},
    {"name": "Цветущие", "description": "Растения с декоративными цветами"},
    {"name": "Красивые листья", "description": "Растения с декоративной листвой"},
    {"name": "Ароматные", "description": "Растения с приятным ароматом"},
    {"name": "Лекарственные", "description": "Растения, используемые в медицине"},
    {"name": "Очищающие воздух", "description": "Растения, улучшающие качество воздуха"},
    {"name": "Ядовитые", "description": "Токсичные растения"},
    {"name": "Съедобные", "description": "Растения, употребляемые в пищу"},
    {"name": "Водные", "description": "Растения для водоемов"},
    {"name": "Засухоустойчивые", "description": "Растения, устойчивые к засухе"},
    {"name": "Зимостойкие", "description": "Растения, переносящие низкие температуры"},
    {"name": "Экзотические", "description": "Необычные или редкие растения"},
    {"name": "Почвопокровные", "description": "Растения для покрытия почвы"},
    {"name": "Вьющиеся", "description": "Растения с вьющимися стеблями"},
    {"name": "Крупномеры", "description": "Высокие или крупные растения"},
    {"name": "Миниатюрные", "description": "Маленькие растения"},
    {"name": "Быстрорастущие", "description": "Растения с быстрым ростом"},
    {"name": "Медленнорастущие", "description": "Растения с медленным ростом"},
]

# Климатические зоны (по USDA)
CLIMATE_ZONES = [
    {
        "name": "Зона 1", 
        "description": "Очень холодный климат", 
        "zone_number": 1, 
        "min_temperature": -51.1, 
        "max_temperature": -45.6
    },
    {
        "name": "Зона 2", 
        "description": "Холодный климат", 
        "zone_number": 2, 
        "min_temperature": -45.6, 
        "max_temperature": -40.0
    },
    {
        "name": "Зона 3", 
        "description": "Холодный климат", 
        "zone_number": 3, 
        "min_temperature": -40.0, 
        "max_temperature": -34.4
    },
    {
        "name": "Зона 4", 
        "description": "Умеренно-холодный климат", 
        "zone_number": 4, 
        "min_temperature": -34.4, 
        "max_temperature": -28.9
    },
    {
        "name": "Зона 5", 
        "description": "Умеренно-холодный климат", 
        "zone_number": 5, 
        "min_temperature": -28.9, 
        "max_temperature": -23.3
    },
    {
        "name": "Зона 6", 
        "description": "Умеренный климат", 
        "zone_number": 6, 
        "min_temperature": -23.3, 
        "max_temperature": -17.8
    },
    {
        "name": "Зона 7", 
        "description": "Умеренный климат", 
        "zone_number": 7, 
        "min_temperature": -17.8, 
        "max_temperature": -12.2
    },
    {
        "name": "Зона 8", 
        "description": "Теплый умеренный климат", 
        "zone_number": 8, 
        "min_temperature": -12.2, 
        "max_temperature": -6.7
    },
    {
        "name": "Зона 9", 
        "description": "Теплый умеренный климат", 
        "zone_number": 9, 
        "min_temperature": -6.7, 
        "max_temperature": -1.1
    },
    {
        "name": "Зона 10", 
        "description": "Теплый климат", 
        "zone_number": 10, 
        "min_temperature": -1.1, 
        "max_temperature": 4.4
    },
    {
        "name": "Зона 11", 
        "description": "Теплый климат", 
        "zone_number": 11, 
        "min_temperature": 4.4, 
        "max_temperature": 10.0
    },
    {
        "name": "Зона 12", 
        "description": "Жаркий климат", 
        "zone_number": 12, 
        "min_temperature": 10.0, 
        "max_temperature": 15.6
    },
    {
        "name": "Зона 13", 
        "description": "Очень жаркий климат", 
        "zone_number": 13, 
        "min_temperature": 15.6, 
        "max_temperature": 21.1
    },
]

# Примеры растений для заполнения базы
PLANTS = [
    {
        "name": "Фикус Бенджамина",
        "latin_name": "Ficus benjamina",
        "description": "Популярное комнатное растение с элегантными листьями. Имеет декоративную форму и легко поддается формированию.",
        "plant_type": PlantType.TREE,
        "life_cycle": LifeCycle.PERENNIAL,
        "height_min": 30,
        "height_max": 300,
        "growth_rate": GrowthRate.MODERATE,
        "popularity_score": 85,
        "flowering_period": "Не цветет в домашних условиях",
        "bloom_color": None,
        "hardiness_zone_min": 10,
        "hardiness_zone_max": 12,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "temperature_min": 15,
        "temperature_max": 30,
        "humidity_level": HumidityLevel.MEDIUM,
        "care_difficulty": CareDifficulty.MODERATE,
        "fertilizing_frequency": FertilizingFrequency.MONTHLY,
        "repotting_frequency": RepottingFrequency.BI_ANNUALLY,
        "is_toxic": True,
        "care_instructions": "Регулярно протирайте листья влажной тканью. Избегайте сквозняков и резких перепадов температуры. Поливайте умеренно, давая почве просохнуть между поливами.",
        "planting_instructions": "Используйте хорошо дренированную почву для комнатных растений. Выберите горшок, который немного больше корневой системы.",
        "pruning_tips": "Обрезку можно проводить весной для формирования кроны. Удаляйте засохшие или поврежденные ветви.",
        "notes": "Фикус Бенджамина может сбрасывать листья при изменении условий, но обычно быстро восстанавливается.",
        "care_tips": json.dumps([
            "Старайтесь не менять положение горшка с растением", 
            "Не допускайте застоя воды в поддоне", 
            "Зимой сократите полив"
        ]),
        "common_problems": json.dumps([
            {"problem": "Опадение листьев", "solution": "Чаще всего связано с изменением условий. Стабилизируйте окружение, избегайте сквозняков и переувлажнения."},
            {"problem": "Пожелтение листьев", "solution": "Может быть вызвано переувлажнением или недостатком освещения. Скорректируйте полив и переместите в более светлое место."},
            {"problem": "Вредители", "solution": "Чаще всего поражается щитовкой и паутинным клещом. Обработайте инсектицидом и регулярно осматривайте растение."}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Черенкование", "description": "Отрежьте здоровый черенок длиной 10-15 см, удалите нижние листья и поместите в воду или влажную почву."},
            {"method": "Воздушные отводки", "description": "Сделайте надрез на стебле, обмотайте влажным мхом и пленкой. Когда появятся корни, отрежьте и посадите."}
        ]),
        "categories": [1, 5],  # ID категорий
        "climate_zones": [10, 11, 12],  # ID климатических зон
        "tags": [1, 2, 5, 8, 9]  # ID тегов
    },
    {
        "name": "Монстера Деликатесная",
        "latin_name": "Monstera deliciosa",
        "description": "Крупное комнатное растение с эффектными резными листьями. Популярно в интерьерном дизайне.",
        "plant_type": PlantType.VINE,
        "life_cycle": LifeCycle.PERENNIAL,
        "height_min": 50,
        "height_max": 300,
        "growth_rate": GrowthRate.MODERATE,
        "popularity_score": 90,
        "flowering_period": "Редко цветет в домашних условиях",
        "bloom_color": "Белый",
        "hardiness_zone_min": 10,
        "hardiness_zone_max": 12,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "temperature_min": 18,
        "temperature_max": 30,
        "humidity_level": HumidityLevel.HIGH,
        "care_difficulty": CareDifficulty.EASY,
        "fertilizing_frequency": FertilizingFrequency.MONTHLY,
        "repotting_frequency": RepottingFrequency.BI_ANNUALLY,
        "is_toxic": True,
        "care_instructions": "Поливайте когда верхний слой почвы высохнет. Регулярно опрыскивайте листья для повышения влажности. Протирайте листья от пыли.",
        "planting_instructions": "Используйте рыхлую, богатую органикой почву с хорошим дренажем. Выберите просторный горшок с дренажными отверстиями.",
        "pruning_tips": "Удаляйте пожелтевшие или поврежденные листья. При необходимости можно обрезать слишком длинные воздушные корни.",
        "notes": "По мере роста растению может потребоваться опора. Воздушные корни не следует полностью обрезать, они помогают растению получать питательные вещества.",
        "care_tips": json.dumps([
            "Предоставьте опору для роста вверх", 
            "Регулярно протирайте крупные листья от пыли", 
            "Поворачивайте горшок для равномерного роста"
        ]),
        "common_problems": json.dumps([
            {"problem": "Пожелтение листьев", "solution": "Обычно вызвано переувлажнением. Дайте почве просохнуть и скорректируйте режим полива."},
            {"problem": "Коричневые кончики листьев", "solution": "Признак низкой влажности. Чаще опрыскивайте растение и/или используйте увлажнитель воздуха."},
            {"problem": "Отсутствие перфорации на листьях", "solution": "Недостаточное освещение. Переместите растение в более светлое место, но избегайте прямых солнечных лучей."}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Черенкование", "description": "Отрежьте черенок с воздушным корнем и 1-2 листьями. Посадите в влажную почву или поместите в воду до появления корней."},
            {"method": "Деление куста", "description": "При пересадке аккуратно разделите корневище на несколько частей, каждая с несколькими листьями."}
        ]),
        "categories": [1, 5],  # ID категорий
        "climate_zones": [10, 11, 12],  # ID климатических зон
        "tags": [1, 5, 8, 9, 14, 17]  # ID тегов
    },
    {
        "name": "Фиалка Узамбарская",
        "latin_name": "Saintpaulia ionantha",
        "description": "Компактное цветущее комнатное растение с мягкими опушенными листьями и яркими цветками различных оттенков.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "height_min": 5,
        "height_max": 15,
        "growth_rate": GrowthRate.MODERATE,
        "popularity_score": 80,
        "flowering_period": "Круглый год при правильном уходе",
        "bloom_color": "Фиолетовый, розовый, белый, синий",
        "hardiness_zone_min": 11,
        "hardiness_zone_max": 12,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "temperature_min": 18,
        "temperature_max": 24,
        "humidity_level": HumidityLevel.MEDIUM,
        "care_difficulty": CareDifficulty.MODERATE,
        "fertilizing_frequency": FertilizingFrequency.BI_WEEKLY,
        "repotting_frequency": RepottingFrequency.ANNUALLY,
        "is_toxic": False,
        "care_instructions": "Поливайте через поддон, не допуская попадания воды на листья. Располагайте в ярком месте без прямых солнечных лучей. Используйте специальные удобрения для фиалок.",
        "planting_instructions": "Используйте легкую, рыхлую почву для фиалок. Выбирайте небольшие горшки, так как фиалки лучше цветут в тесной посуде.",
        "pruning_tips": "Удаляйте увядшие цветы и пожелтевшие листья. Периодически прореживайте растение, удаляя старые внешние листья.",
        "notes": "Фиалки чувствительны к холодной воде и сквознякам. Для стимуляции цветения используйте специальные подкормки с фосфором.",
        "care_tips": json.dumps([
            "Используйте теплую отстоянную воду для полива", 
            "Избегайте попадания воды на листья и центр розетки", 
            "Располагайте на восточных или западных окнах"
        ]),
        "common_problems": json.dumps([
            {"problem": "Отсутствие цветения", "solution": "Недостаточное освещение или питание. Переместите в более светлое место и используйте удобрения для цветущих растений."},
            {"problem": "Вытягивание розетки", "solution": "Недостаток света. Переместите на более светлое место и регулярно поворачивайте растение."},
            {"problem": "Гниение центра розетки", "solution": "Попадание воды в центр розетки. Поливайте через поддон и следите, чтобы вода не попадала на листья."}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Листовые черенки", "description": "Отделите здоровый лист с черешком, посадите черешок в легкую почву и накройте прозрачным колпаком для создания повышенной влажности."},
            {"method": "Деление куста", "description": "Аккуратно разделите растение на несколько розеток при пересадке."}
        ]),
        "categories": [1, 4],  # ID категорий
        "climate_zones": [11, 12],  # ID климатических зон
        "tags": [1, 3, 4, 18]  # ID тегов
    },
    {
        "name": "Алоэ Вера",
        "latin_name": "Aloe vera",
        "description": "Суккулент с толстыми мясистыми листьями, известный своими лечебными свойствами.",
        "plant_type": PlantType.SUCCULENT,
        "life_cycle": LifeCycle.PERENNIAL,
        "height_min": 20,
        "height_max": 60,
        "growth_rate": GrowthRate.SLOW,
        "popularity_score": 85,
        "flowering_period": "Весна-лето",
        "bloom_color": "Желтый, оранжевый",
        "hardiness_zone_min": 9,
        "hardiness_zone_max": 11,
        "watering_frequency": WateringFrequency.BI_WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "temperature_min": 10,
        "temperature_max": 30,
        "humidity_level": HumidityLevel.LOW,
        "care_difficulty": CareDifficulty.VERY_EASY,
        "fertilizing_frequency": FertilizingFrequency.QUARTERLY,
        "repotting_frequency": RepottingFrequency.BI_ANNUALLY,
        "is_toxic": False,
        "care_instructions": "Поливайте только когда почва полностью высохнет. Обеспечьте яркое освещение. Зимой сократите полив и поддерживайте температуру не ниже 10°C.",
        "planting_instructions": "Используйте хорошо дренированную почву для суккулентов. Горшок должен иметь дренажные отверстия.",
        "pruning_tips": "Удаляйте засохшие или поврежденные листья. Срезайте листья у основания для использования геля.",
        "notes": "Гель алоэ вера широко используется в косметологии и медицине. Растение считается лекарственным и имеет множество применений.",
        "care_tips": json.dumps([
            "Поливайте редко, но обильно", 
            "Располагайте на солнечном подоконнике", 
            "Зимой сократите полив до минимума"
        ]),
        "common_problems": json.dumps([
            {"problem": "Мягкие или коричневые листья", "solution": "Признак переувлажнения. Сократите полив и проверьте дренаж."},
            {"problem": "Тонкие, вытянутые листья", "solution": "Недостаток освещения. Переместите растение в более солнечное место."},
            {"problem": "Коричневые кончики листьев", "solution": "Слишком сухой воздух или недостаток полива. Проверьте режим ухода."}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Боковые побеги", "description": "Аккуратно отделите боковые побеги (детки) с корнями и посадите в отдельные горшки."},
            {"method": "Листовые черенки", "description": "В редких случаях можно укоренить срезанный лист, но это менее эффективный метод."}
        ]),
        "categories": [1, 6],  # ID категорий
        "climate_zones": [9, 10, 11],  # ID климатических зон
        "tags": [1, 3, 7, 10, 12]  # ID тегов
    },
    {
        "name": "Роза Чайная",
        "latin_name": "Rosa x odorata",
        "description": "Красивое цветущее садовое растение с ароматными цветками различных оттенков.",
        "plant_type": PlantType.SHRUB,
        "life_cycle": LifeCycle.PERENNIAL,
        "height_min": 60,
        "height_max": 180,
        "growth_rate": GrowthRate.MODERATE,
        "popularity_score": 95,
        "flowering_period": "Май-Октябрь",
        "bloom_color": "Различные оттенки: красный, розовый, желтый, белый",
        "hardiness_zone_min": 6,
        "hardiness_zone_max": 9,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "temperature_min": -10,
        "temperature_max": 35,
        "humidity_level": HumidityLevel.MEDIUM,
        "care_difficulty": CareDifficulty.MODERATE,
        "fertilizing_frequency": FertilizingFrequency.MONTHLY,
        "repotting_frequency": RepottingFrequency.RARELY,
        "is_toxic": False,
        "care_instructions": "Поливайте под корень, избегая попадания воды на листья. Подкармливайте специальными удобрениями для роз. На зиму укрывайте в холодных регионах.",
        "planting_instructions": "Сажайте в хорошо дренированную, плодородную почву. Выбирайте солнечное место, защищенное от сильных ветров.",
        "pruning_tips": "Обрезайте ранней весной, удаляя мертвые и слабые побеги. Формирующую обрезку проводите после первой волны цветения.",
        "notes": "Розы требуют регулярного ухода и защиты от вредителей и болезней, но при правильном уходе будут радовать цветением много лет.",
        "care_tips": json.dumps([
            "Поливайте под корень, избегая листьев", 
            "Мульчируйте почву вокруг куста", 
            "Регулярно осматривайте на наличие вредителей"
        ]),
        "common_problems": json.dumps([
            {"problem": "Мучнистая роса", "solution": "Обработайте фунгицидом и обеспечьте хорошую циркуляцию воздуха вокруг куста."},
            {"problem": "Тля", "solution": "Обработайте инсектицидом или смойте сильной струей воды. Привлекайте в сад естественных хищников."},
            {"problem": "Черная пятнистость", "solution": "Удалите пораженные листья, обработайте фунгицидом и улучшите циркуляцию воздуха."}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Черенкование", "description": "Нарежьте полуодревесневшие черенки в начале лета, обработайте стимулятором корнеобразования и посадите в рыхлую почву."},
            {"method": "Прививка", "description": "Профессиональный метод размножения сортовых роз, требующий специальных навыков."}
        ]),
        "categories": [2, 11],  # ID категорий
        "climate_zones": [6, 7, 8, 9],  # ID климатических зон
        "tags": [3, 4, 6, 13]  # ID тегов
    },
]

# Добавим еще 15 растений (упрощенные данные)
MORE_PLANTS = [
    {
        "name": "Хлорофитум Хохлатый",
        "latin_name": "Chlorophytum comosum",
        "description": "Неприхотливое комнатное растение с узкими дугообразными листьями и воздушными отводками.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "care_difficulty": CareDifficulty.VERY_EASY,
        "is_toxic": False,
        "categories": [1, 5],
        "tags": [1, 2, 8]
    },
    {
        "name": "Спатифиллум",
        "latin_name": "Spathiphyllum wallisii",
        "description": "Популярное комнатное растение с глянцевыми темно-зелеными листьями и белыми соцветиями.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": True,
        "categories": [1, 4],
        "tags": [1, 2, 4, 8]
    },
    {
        "name": "Драцена Окаймленная",
        "latin_name": "Dracaena marginata",
        "description": "Древовидное комнатное растение с тонкими изогнутыми листьями на стволах различной высоты.",
        "plant_type": PlantType.TREE,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.BI_WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": True,
        "categories": [1, 5],
        "tags": [1, 5, 8]
    },
    {
        "name": "Кактус Золотой Шар",
        "latin_name": "Echinocactus grusonii",
        "description": "Шаровидный кактус с выраженными ребрами и золотистыми колючками.",
        "plant_type": PlantType.SUCCULENT,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.MONTHLY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.VERY_EASY,
        "is_toxic": False,
        "categories": [1, 6],
        "tags": [1, 3, 12, 14]
    },
    {
        "name": "Замиокулькас",
        "latin_name": "Zamioculcas zamiifolia",
        "description": "Неприхотливое комнатное растение с глянцевыми перистыми листьями, устойчивое к засухе.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.MONTHLY,
        "light_level": LightLevel.LOW_LIGHT,
        "care_difficulty": CareDifficulty.VERY_EASY,
        "is_toxic": True,
        "categories": [1, 5],
        "tags": [1, 2, 5, 12]
    },
    {
        "name": "Лавр Благородный",
        "latin_name": "Laurus nobilis",
        "description": "Вечнозеленое ароматное дерево или кустарник, используемое как пряность.",
        "plant_type": PlantType.TREE,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "care_difficulty": CareDifficulty.MODERATE,
        "is_toxic": False,
        "categories": [2, 17],
        "tags": [3, 6, 7, 10, 13]
    },
    {
        "name": "Базилик Обыкновенный",
        "latin_name": "Ocimum basilicum",
        "description": "Ароматная кулинарная трава с яркими зелеными листьями.",
        "plant_type": PlantType.HERB,
        "life_cycle": LifeCycle.ANNUAL,
        "watering_frequency": WateringFrequency.DAILY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": False,
        "categories": [3, 17],
        "tags": [3, 6, 7, 10, 19]
    },
    {
        "name": "Томат Черри",
        "latin_name": "Solanum lycopersicum var. cerasiforme",
        "description": "Сорт томатов с небольшими сладкими плодами размером с вишню.",
        "plant_type": PlantType.VEGETABLE,
        "life_cycle": LifeCycle.ANNUAL,
        "watering_frequency": WateringFrequency.DAILY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.MODERATE,
        "is_toxic": False,
        "categories": [3, 15],
        "tags": [3, 10, 19]
    },
    {
        "name": "Орхидея Фаленопсис",
        "latin_name": "Phalaenopsis",
        "description": "Популярная эпифитная орхидея с длительным и эффектным цветением.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.PARTIAL_SUN,
        "care_difficulty": CareDifficulty.MODERATE,
        "is_toxic": False,
        "categories": [1, 4],
        "tags": [4, 14]
    },
    {
        "name": "Земляника Садовая",
        "latin_name": "Fragaria × ananassa",
        "description": "Многолетнее травянистое растение с вкусными ягодами.",
        "plant_type": PlantType.FRUIT,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": False,
        "categories": [3, 16],
        "tags": [3, 10, 13, 15]
    },
    {
        "name": "Нефролепис Возвышенный",
        "latin_name": "Nephrolepis exaltata",
        "description": "Папоротник с изящными перистыми листьями, часто используемый как комнатное растение.",
        "plant_type": PlantType.FERN,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.SHADE,
        "care_difficulty": CareDifficulty.MODERATE,
        "is_toxic": False,
        "categories": [1, 8],
        "tags": [2, 5, 8]
    },
    {
        "name": "Сансевиерия",
        "latin_name": "Sansevieria trifasciata",
        "description": "Неприхотливое комнатное растение с жесткими вертикальными листьями, очищающее воздух.",
        "plant_type": PlantType.SUCCULENT,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.MONTHLY,
        "light_level": LightLevel.LOW_LIGHT,
        "care_difficulty": CareDifficulty.VERY_EASY,
        "is_toxic": True,
        "categories": [1, 5],
        "tags": [1, 2, 5, 8, 12]
    },
    {
        "name": "Туя Западная",
        "latin_name": "Thuja occidentalis",
        "description": "Вечнозеленое хвойное дерево или кустарник, часто используемое в ландшафтном дизайне.",
        "plant_type": PlantType.TREE,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.BI_WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": False,
        "categories": [2, 10],
        "tags": [3, 5, 13, 20]
    },
    {
        "name": "Барбарис Тунберга",
        "latin_name": "Berberis thunbergii",
        "description": "Декоративный кустарник с яркой листвой и красными ягодами.",
        "plant_type": PlantType.SHRUB,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": False,
        "categories": [2, 9],
        "tags": [3, 5, 13]
    },
    {
        "name": "Тюльпан",
        "latin_name": "Tulipa",
        "description": "Луковичное растение с яркими весенними цветами различных оттенков.",
        "plant_type": PlantType.FLOWER,
        "life_cycle": LifeCycle.PERENNIAL,
        "watering_frequency": WateringFrequency.WEEKLY,
        "light_level": LightLevel.FULL_SUN,
        "care_difficulty": CareDifficulty.EASY,
        "is_toxic": False,
        "categories": [2, 14],
        "tags": [3, 4, 13]
    },
]

# Добавляем упрощенные растения в общий список
for plant in MORE_PLANTS:
    # Устанавливаем значения по умолчанию для необязательных полей
    default_plant = {
        "height_min": random.randint(10, 50),
        "height_max": random.randint(60, 200),
        "growth_rate": random.choice(list(GrowthRate)),
        "popularity_score": random.randint(60, 90),
        "flowering_period": None,
        "bloom_color": None,
        "hardiness_zone_min": random.randint(5, 9),
        "hardiness_zone_max": random.randint(10, 13),
        "temperature_min": random.randint(5, 15),
        "temperature_max": random.randint(25, 35),
        "humidity_level": random.choice(list(HumidityLevel)),
        "fertilizing_frequency": random.choice(list(FertilizingFrequency)),
        "repotting_frequency": random.choice(list(RepottingFrequency)),
        "care_instructions": f"Общие рекомендации по уходу за {plant['name']}",
        "planting_instructions": "Инструкции по посадке",
        "pruning_tips": "Советы по обрезке",
        "notes": f"Дополнительная информация о {plant['name']}",
        "care_tips": json.dumps([f"Совет по уходу 1 для {plant['name']}", f"Совет по уходу 2 для {plant['name']}"]),
        "common_problems": json.dumps([
            {"problem": "Проблема 1", "solution": "Решение 1"},
            {"problem": "Проблема 2", "solution": "Решение 2"}
        ]),
        "propagation_methods": json.dumps([
            {"method": "Метод 1", "description": "Описание метода 1"},
            {"method": "Метод 2", "description": "Описание метода 2"}
        ]),
        "climate_zones": random.sample(range(1, len(CLIMATE_ZONES) + 1), k=random.randint(1, 3))
    }
    
    # Объединяем словари, приоритет отдаем ключам из plant
    complete_plant = {**default_plant, **plant}
    PLANTS.append(complete_plant)

# Изображения для растений
PLANT_IMAGES = [
    {
        "plant_id": 1,  # Фикус Бенджамина
        "url": "https://example.com/images/ficus-benjamina-1.jpg",
        "alt": "Фикус Бенджамина в горшке",
        "title": "Взрослое растение фикуса Бенджамина",
        "description": "Взрослый фикус Бенджамина с глянцевыми зелеными листьями",
        "thumbnail_url": "https://example.com/images/thumbnails/ficus-benjamina-1.jpg",
        "is_primary": True
    },
    {
        "plant_id": 1,
        "url": "https://example.com/images/ficus-benjamina-2.jpg",
        "alt": "Листья фикуса Бенджамина крупным планом",
        "title": "Листья фикуса Бенджамина",
        "description": "Крупный план листьев фикуса Бенджамина",
        "thumbnail_url": "https://example.com/images/thumbnails/ficus-benjamina-2.jpg",
        "is_primary": False
    },
    {
        "plant_id": 2,  # Монстера
        "url": "https://example.com/images/monstera-deliciosa-1.jpg",
        "alt": "Монстера Деликатесная с перфорированными листьями",
        "title": "Взрослая Монстера Деликатесная",
        "description": "Взрослое растение монстеры с крупными перфорированными листьями",
        "thumbnail_url": "https://example.com/images/thumbnails/monstera-deliciosa-1.jpg",
        "is_primary": True
    },
    {
        "plant_id": 2,
        "url": "https://example.com/images/monstera-deliciosa-2.jpg",
        "alt": "Молодое растение монстеры",
        "title": "Молодая Монстера Деликатесная",
        "description": "Молодое растение монстеры без перфорации листьев",
        "thumbnail_url": "https://example.com/images/thumbnails/monstera-deliciosa-2.jpg",
        "is_primary": False
    },
]

# Добавляем изображения для всех растений
for i in range(3, len(PLANTS) + 1):
    PLANT_IMAGES.append({
        "plant_id": i,
        "url": f"https://example.com/images/plant-{i}-1.jpg",
        "alt": f"Изображение {PLANTS[i-1]['name']}",
        "title": f"{PLANTS[i-1]['name']}",
        "description": f"Фотография растения {PLANTS[i-1]['name']}",
        "thumbnail_url": f"https://example.com/images/thumbnails/plant-{i}-1.jpg",
        "is_primary": True
    })
    
    # Добавляем второе изображение для некоторых растений
    if random.random() > 0.5:
        PLANT_IMAGES.append({
            "plant_id": i,
            "url": f"https://example.com/images/plant-{i}-2.jpg",
            "alt": f"Дополнительное изображение {PLANTS[i-1]['name']}",
            "title": f"{PLANTS[i-1]['name']} - деталь",
            "description": f"Детальная фотография {PLANTS[i-1]['name']}",
            "thumbnail_url": f"https://example.com/images/thumbnails/plant-{i}-2.jpg",
            "is_primary": False
        })

# Вопросы пользователей о растениях
QUESTIONS = [
    {
        "title": "Как часто поливать фикус Бенджамина?",
        "body": "Недавно приобрел фикус Бенджамина. Не могу понять, как часто его нужно поливать. Сейчас стоит на восточном окне. Листья начали желтеть и опадать. Что я делаю не так?",
        "author_id": 3,  # ID пользователя
        "plant_id": 1,  # ID растения (фикус)
        "is_solved": False,
        "view_count": 45,
        "votes_up": 5,
        "votes_down": 0
    },
    {
        "title": "Монстера не формирует перфорацию на листьях",
        "body": "Моей монстере около года, но листья до сих пор без перфорации. Растение здоровое, выпускает новые листья, но они все без отверстий. Стоит у окна, но прямых солнечных лучей нет. Что может быть причиной?",
        "author_id": 5,
        "plant_id": 2,  # ID растения (монстера)
        "is_solved": True,
        "view_count": 87,
        "votes_up": 10,
        "votes_down": 1
    },
    {
        "title": "Оптимальная почва для фиалок",
        "body": "Какую почву лучше использовать для фиалок? Можно ли использовать обычный грунт для комнатных растений или нужен специальный субстрат? Поделитесь опытом успешного выращивания.",
        "author_id": 7,
        "plant_id": 3,  # ID растения (фиалка)
        "is_solved": True,
        "view_count": 65,
        "votes_up": 8,
        "votes_down": 0
    },
    {
        "title": "Алоэ желтеет и становится мягким",
        "body": "Мое алоэ начало желтеть и листья стали мягкими на ощупь. Поливаю раз в две недели небольшим количеством воды. Стоит на южном окне. Что может быть причиной и как спасти растение?",
        "author_id": 4,
        "plant_id": 4,  # ID растения (алоэ)
        "is_solved": False,
        "view_count": 32,
        "votes_up": 3,
        "votes_down": 0
    },
    {
        "title": "Когда лучше обрезать розы?",
        "body": "У меня в саду несколько кустов чайных роз. Когда лучше проводить обрезку - осенью или весной? И как правильно формировать куст для лучшего цветения?",
        "author_id": 6,
        "plant_id": 5,  # ID растения (роза)
        "is_solved": True,
        "view_count": 120,
        "votes_up": 15,
        "votes_down": 1
    },
]

# Добавим еще вопросов для других растений
for i in range(6, min(16, len(PLANTS) + 1)):
    QUESTIONS.append({
        "title": f"Вопрос о {PLANTS[i-1]['name']}",
        "body": f"У меня проблема с растением {PLANTS[i-1]['name']}. [Описание проблемы]",
        "author_id": random.randint(3, len(USERS)),
        "plant_id": i,
        "is_solved": random.choice([True, False]),
        "view_count": random.randint(10, 100),
        "votes_up": random.randint(0, 10),
        "votes_down": random.randint(0, 2)
    })

# Добавим общие вопросы без привязки к конкретному растению
GENERAL_QUESTIONS = [
    {
        "title": "Лучшие растения для северных окон",
        "body": "Подскажите, какие комнатные растения будут хорошо расти на северном окне с ограниченным освещением? Хочется что-то неприхотливое, но при этом декоративное.",
        "author_id": 8,
        "plant_id": None,
        "is_solved": False,
        "view_count": 67,
        "votes_up": 7,
        "votes_down": 0
    },
    {
        "title": "Как защитить растения от домашних животных?",
        "body": "У меня кошка, которая любит грызть комнатные растения. Посоветуйте, какие растения нетоксичны для кошек и какие методы можно использовать, чтобы отучить питомца от поедания листьев?",
        "author_id": 9,
        "plant_id": None,
        "is_solved": True,
        "view_count": 92,
        "votes_up": 12,
        "votes_down": 1
    },
    {
        "title": "Признаки переувлажнения почвы",
        "body": "Как определить, что растение переувлажнено? Какие признаки указывают на избыток влаги и как спасти растение, если оно уже начало страдать от перелива?",
        "author_id": 10,
        "plant_id": None,
        "is_solved": True,
        "view_count": 105,
        "votes_up": 18,
        "votes_down": 0
    },
]

# Добавляем общие вопросы в основной список
QUESTIONS.extend(GENERAL_QUESTIONS)

# Ответы на вопросы
ANSWERS = [
    {
        "body": "Фикус Бенджамина нужно поливать, когда верхний слой почвы (примерно 2-3 см) полностью высохнет. Обычно это происходит раз в 7-10 дней, в зависимости от условий содержания. Желтеющие и опадающие листья часто говорят о переувлажнении. Убедитесь, что в горшке есть дренажные отверстия и вода не застаивается в поддоне. Также фикус не любит сквозняков и резких перепадов температуры.",
        "author_id": 3,  # ID пользователя
        "question_id": 1,  # ID вопроса
        "is_accepted": False,
        "votes_up": 3,
        "votes_down": 0
    },
    {
        "body": "Перфорация листьев монстеры напрямую зависит от освещения. Если его недостаточно, листья остаются цельными. Переместите растение ближе к окну, но избегайте прямых солнечных лучей, которые могут обжечь листья. Также на формирование перфорации влияет возраст растения - чем старше монстера, тем более выраженные прорези образуются на листьях. Дополнительно рекомендую подкармливать растение удобрениями для декоративно-лиственных растений в период активного роста.",
        "author_id": 3,  # ID пользователя (plant_expert)
        "question_id": 2,  # ID вопроса
        "is_accepted": True,
        "votes_up": 8,
        "votes_down": 0
    },
    {
        "body": "Для фиалок лучше использовать специальный субстрат, так как они предъявляют особые требования к почве. Идеальный грунт должен быть легким, воздухопроницаемым и слабокислым (pH 5.5-6.5). Можно приготовить смесь самостоятельно: 2 части торфа, 1 часть перлита и 1 часть вермикулита. В готовый магазинный грунт для фиалок обычно уже добавлены все необходимые компоненты. Важно, чтобы почва хорошо пропускала воду и воздух к корням.",
        "author_id": 2,  # ID пользователя (модератор)
        "question_id": 3,  # ID вопроса
        "is_accepted": True,
        "votes_up": 5,
        "votes_down": 0
    },
    {
        "body": "Мягкие и желтеющие листья алоэ - классический признак переувлажнения. Несмотря на то, что вы поливаете нечасто, возможно, почва слишком долго остается влажной. Проверьте, хороший ли дренаж в горшке. Алоэ нужна почва, которая быстро высыхает. Рекомендую использовать смесь для кактусов и суккулентов с добавлением песка или перлита. Прекратите полив до полного высыхания почвы, затем поливайте очень умеренно. Также стоит проверить, не стоит ли растение в слишком жарком месте под прямыми солнечными лучами - это тоже может вызывать пожелтение.",
        "author_id": 3,  # ID пользователя (plant_expert)
        "question_id": 4,  # ID вопроса
        "is_accepted": False,
        "votes_up": 2,
        "votes_down": 0
    },
    {
        "body": "Лучшее время для обрезки роз зависит от вашего климата. В большинстве регионов рекомендуется проводить основную обрезку ранней весной, когда почки начинают набухать, но еще не распустились (обычно в марте-апреле). Это позволяет избежать зимних повреждений и стимулирует активный рост. Удалите все мертвые, поврежденные и слабые побеги, а также те, что растут внутрь куста. Для хорошего цветения оставляйте побеги толщиной не менее карандаша и обрезайте на высоте 30-45 см от земли, делая срез под углом над наружной почкой. После первой волны цветения можно провести легкую обрезку, удалив отцветшие бутоны, чтобы стимулировать повторное цветение.",
        "author_id": 3,  # ID пользователя (plant_expert)
        "question_id": 5,  # ID вопроса
        "is_accepted": True,
        "votes_up": 12,
        "votes_down": 0
    },
]

# Добавляем ответы на остальные вопросы
for i in range(6, len(QUESTIONS) + 1):
    expert_response = {
        "body": f"Профессиональный ответ на вопрос о {QUESTIONS[i-1]['title'].lower()}. [Детальное объяснение проблемы и способов ее решения]",
        "author_id": 3,  # Expert user
        "question_id": i,
        "is_accepted": QUESTIONS[i-1]["is_solved"],
        "votes_up": random.randint(1, 10),
        "votes_down": random.randint(0, 2)
    }
    ANSWERS.append(expert_response)
    
    # Для некоторых вопросов добавим дополнительные ответы
    if random.random() > 0.5:
        additional_response = {
            "body": f"Альтернативное мнение или дополнительная информация по вопросу о {QUESTIONS[i-1]['title'].lower()}. [Другой подход к решению]",
            "author_id": random.choice([u for u in range(4, len(USERS) + 1) if u != 3]),  # Не эксперт
            "question_id": i,
            "is_accepted": False,
            "votes_up": random.randint(0, 5),
            "votes_down": random.randint(0, 3)
        }
        ANSWERS.append(additional_response)

# Голоса за вопросы
QUESTION_VOTES = []
for question_id in range(1, len(QUESTIONS) + 1):
    # Случайное количество голосов за вопрос
    num_votes = random.randint(QUESTIONS[question_id-1]["votes_up"] + QUESTIONS[question_id-1]["votes_down"], 
                              QUESTIONS[question_id-1]["votes_up"] + QUESTIONS[question_id-1]["votes_down"] + 5)
    
    for _ in range(num_votes):
        # Выбираем случайного пользователя
        user_id = random.randint(1, len(USERS))
        
        # Определяем, голос "за" или "против", с учетом существующего соотношения
        if random.random() < 0.8:  # 80% шанс голоса "за"
            vote_type = VoteType.UP
        else:
            vote_type = VoteType.DOWN
        
        vote = {
            "user_id": user_id,
            "question_id": question_id,
            "vote_type": vote_type
        }
        
        # Проверяем, не голосовал ли уже этот пользователь за этот вопрос
        if not any(v["user_id"] == user_id and v["question_id"] == question_id for v in QUESTION_VOTES):
            QUESTION_VOTES.append(vote)

# Голоса за ответы
ANSWER_VOTES = []
for answer_id in range(1, len(ANSWERS) + 1):
    # Случайное количество голосов за ответ
    num_votes = random.randint(ANSWERS[answer_id-1]["votes_up"] + ANSWERS[answer_id-1]["votes_down"], 
                              ANSWERS[answer_id-1]["votes_up"] + ANSWERS[answer_id-1]["votes_down"] + 5)
    
    for _ in range(num_votes):
        # Выбираем случайного пользователя
        user_id = random.randint(1, len(USERS))
        
        # Определяем, голос "за" или "против", с учетом существующего соотношения
        if random.random() < 0.8:  # 80% шанс голоса "за"
            vote_type = VoteType.UP
        else:
            vote_type = VoteType.DOWN
        
        vote = {
            "user_id": user_id,
            "answer_id": answer_id,
            "vote_type": vote_type
        }
        
        # Проверяем, не голосовал ли уже этот пользователь за этот ответ
        if not any(v["user_id"] == user_id and v["answer_id"] == answer_id for v in ANSWER_VOTES):
            ANSWER_VOTES.append(vote)


# Функции для заполнения базы данных

async def create_tables():
    """Создание таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_permissions():
    """Создание разрешений"""
    async with async_session() as session:
        for perm_data in PERMISSIONS:
            permission = Permission(
                name=perm_data["name"],
                description=perm_data.get("description")
            )
            session.add(permission)
        await session.commit()


async def create_roles():
    """Создание ролей и связывание с разрешениями"""
    async with async_session() as session:
        # Получаем все созданные разрешения
        result = await session.execute(sa.select(Permission))
        permissions = {perm.name: perm for perm in result.scalars().all()}
        
        for role_data in ROLES:
            # Создаем роль
            role = Role(
                name=role_data["name"],
                description=role_data.get("description")
            )
            
            # Связываем с разрешениями
            for perm_name in role_data["permissions"]:
                if perm_name in permissions:
                    role.permissions.append(permissions[perm_name])
            
            session.add(role)
        
        await session.commit()


async def create_users():
    """Создание пользователей и связывание с ролями"""
    async with async_session() as session:
        # Получаем все созданные роли
        result = await session.execute(sa.select(Role))
        roles = {role.name: role for role in result.scalars().all()}
        
        for user_data in USERS:
            # Хешируем пароль
            hashed_password = pwd_context.hash(user_data["password"])
            
            # Создаем пользователя
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                hashed_password=hashed_password,
                is_active=user_data.get("is_active", True),
                is_verified=user_data.get("is_verified", False),
                privacy_level=user_data.get("privacy_level", PrivacyLevel.LIMITED),
                avatar_url=user_data.get("avatar_url")
            )
            
            # Связываем с ролями
            for role_name in user_data.get("roles", []):
                if role_name in roles:
                    user.roles.append(roles[role_name])
            
            session.add(user)
        
        await session.commit()


async def create_categories():
    """Создание категорий растений"""
    async with async_session() as session:
        # Первый проход: создаем все категории с parent_id=None
        for i, category_data in enumerate(PLANT_CATEGORIES, 1):
            if category_data["parent_id"] is None:
                category = PlantCategory(
                    name=category_data["name"],
                    description=category_data.get("description")
                )
                session.add(category)
        
        await session.commit()
        
        # Второй проход: обновляем категории с parent_id
        for i, category_data in enumerate(PLANT_CATEGORIES, 1):
            if category_data["parent_id"] is not None:
                # Получаем id родительской категории
                result = await session.execute(
                    sa.select(PlantCategory.id)
                    .where(PlantCategory.name == PLANT_CATEGORIES[category_data["parent_id"] - 1]["name"])
                )
                parent_id = result.scalar_one()
                
                category = PlantCategory(
                    name=category_data["name"],
                    description=category_data.get("description"),
                    parent_id=parent_id
                )
                session.add(category)
        
        await session.commit()


async def create_tags():
    """Создание тегов для растений"""
    async with async_session() as session:
        for tag_data in TAGS:
            tag = Tag(
                name=tag_data["name"],
                description=tag_data.get("description")
            )
            session.add(tag)
        
        await session.commit()


async def create_climate_zones():
    """Создание климатических зон"""
    async with async_session() as session:
        for zone_data in CLIMATE_ZONES:
            zone = ClimateZone(
                name=zone_data["name"],
                description=zone_data.get("description"),
                zone_number=zone_data["zone_number"],
                min_temperature=zone_data.get("min_temperature"),
                max_temperature=zone_data.get("max_temperature")
            )
            session.add(zone)
        
        await session.commit()


async def create_plants():
    """Создание растений и связывание с категориями, тегами и климатическими зонами"""
    async with async_session() as session:
        for plant_data in PLANTS:
            # Создаем базовое растение
            plant = Plant(
                name=plant_data["name"],
                latin_name=plant_data.get("latin_name"),
                description=plant_data.get("description"),
                plant_type=plant_data.get("plant_type"),
                life_cycle=plant_data.get("life_cycle"),
                height_min=plant_data.get("height_min"),
                height_max=plant_data.get("height_max"),
                growth_rate=plant_data.get("growth_rate"),
                popularity_score=plant_data.get("popularity_score", 0),
                flowering_period=plant_data.get("flowering_period"),
                bloom_color=plant_data.get("bloom_color"),
                hardiness_zone_min=plant_data.get("hardiness_zone_min"),
                hardiness_zone_max=plant_data.get("hardiness_zone_max"),
                watering_frequency=plant_data.get("watering_frequency"),
                light_level=plant_data.get("light_level"),
                temperature_min=plant_data.get("temperature_min"),
                temperature_max=plant_data.get("temperature_max"),
                humidity_level=plant_data.get("humidity_level"),
                care_difficulty=plant_data.get("care_difficulty"),
                fertilizing_frequency=plant_data.get("fertilizing_frequency"),
                repotting_frequency=plant_data.get("repotting_frequency"),
                is_toxic=plant_data.get("is_toxic", False),
                care_instructions=plant_data.get("care_instructions"),
                planting_instructions=plant_data.get("planting_instructions"),
                pruning_tips=plant_data.get("pruning_tips"),
                notes=plant_data.get("notes"),
                care_tips=plant_data.get("care_tips"),
                common_problems=plant_data.get("common_problems"),
                propagation_methods=plant_data.get("propagation_methods")
            )
            
            session.add(plant)
            await session.flush()  # чтобы получить id растения
            
            # Связываем с категориями
            for category_id in plant_data.get("categories", []):
                plant_category = PlantToCategory(
                    plant_id=plant.id,
                    category_id=category_id
                )
                session.add(plant_category)
            
            # Связываем с климатическими зонами
            for zone_id in plant_data.get("climate_zones", []):
                plant_zone = PlantToClimateZone(
                    plant_id=plant.id,
                    climate_zone_id=zone_id
                )
                session.add(plant_zone)
            
            # Связываем с тегами
            for tag_id in plant_data.get("tags", []):
                await session.execute(
                    sa.insert(plant_tag).values(
                        plant_id=plant.id,
                        tag_id=tag_id
                    )
                )
        
        await session.commit()


async def create_plant_images():
    """Создание изображений растений"""
    async with async_session() as session:
        for image_data in PLANT_IMAGES:
            image = PlantImage(
                plant_id=image_data["plant_id"],
                url=image_data["url"],
                alt=image_data.get("alt"),
                title=image_data.get("title"),
                description=image_data.get("description"),
                thumbnail_url=image_data.get("thumbnail_url"),
                is_primary=image_data.get("is_primary", False)
            )
            session.add(image)
        
        await session.commit()


async def create_questions():
    """Создание вопросов пользователей"""
    async with async_session() as session:
        for question_data in QUESTIONS:
            question = Question(
                title=question_data["title"],
                body=question_data["body"],
                author_id=question_data["author_id"],
                plant_id=question_data.get("plant_id"),
                is_solved=question_data.get("is_solved", False),
                view_count=question_data.get("view_count", 0),
                votes_up=question_data.get("votes_up", 0),
                votes_down=question_data.get("votes_down", 0)
            )
            session.add(question)
        
        await session.commit()


async def create_answers():
    """Создание ответов на вопросы"""
    async with async_session() as session:
        for answer_data in ANSWERS:
            answer = Answer(
                body=answer_data["body"],
                author_id=answer_data["author_id"],
                question_id=answer_data["question_id"],
                is_accepted=answer_data.get("is_accepted", False),
                votes_up=answer_data.get("votes_up", 0),
                votes_down=answer_data.get("votes_down", 0)
            )
            session.add(answer)
        
        await session.commit()


async def create_votes():
    """Создание голосов за вопросы и ответы"""
    async with async_session() as session:
        # Голоса за вопросы
        for vote_data in QUESTION_VOTES:
            vote = QuestionVote(
                user_id=vote_data["user_id"],
                question_id=vote_data["question_id"],
                vote_type=vote_data["vote_type"]
            )
            session.add(vote)
        
        # Голоса за ответы
        for vote_data in ANSWER_VOTES:
            vote = AnswerVote(
                user_id=vote_data["user_id"],
                answer_id=vote_data["answer_id"],
                vote_type=vote_data["vote_type"]
            )
            session.add(vote)
        
        await session.commit()


async def seed_database():
    """Заполнение базы данных тестовыми данными"""
    print("Создание таблиц...")
    await create_tables()
    
    print("Создание разрешений...")
    await create_permissions()
    
    print("Создание ролей...")
    await create_roles()
    
    print("Создание пользователей...")
    await create_users()
    
    print("Создание категорий растений...")
    await create_categories()
    
    print("Создание тегов...")
    await create_tags()
    
    print("Создание климатических зон...")
    await create_climate_zones()
    
    print("Создание растений...")
    await create_plants()
    
    print("Создание изображений растений...")
    await create_plant_images()
    
    print("Создание вопросов...")
    await create_questions()
    
    print("Создание ответов...")
    await create_answers()
    
    print("Создание голосов...")
    await create_votes()
    
    print("База данных успешно заполнена!")


if __name__ == "__main__":
    asyncio.run(seed_database())