import asyncio
import json
import sys
import os
from datetime import datetime

# Добавляем путь к приложению в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.infrastructure.database.connection import get_db
from app.domain.models.plant_category import PlantCategory
from app.domain.models.climate_zone import ClimateZone
from app.domain.models.tag import Tag
from app.domain.models.plant import Plant
from app.domain.models.plant_image import PlantImage


async def seed_basic_plants_data():
    """Упрощенная версия заполнения для устранения проблем с timestamps"""
    async for session in get_db():
        try:
            print("🌱 Начинаем безопасное заполнение базы данных...")
            
            # Проверяем, есть ли уже данные
            existing_plants = await session.execute(text("SELECT COUNT(*) FROM plants"))
            if existing_plants.scalar() > 0:
                print("❓ В базе уже есть растения. Продолжить? (y/N)")
                if input().lower() != 'y':
                    print("❌ Операция отменена")
                    return
            
            now = datetime.utcnow()
            
            # 1. Создаем категории
            categories_data = [
                {"name": "Лиственные", "description": "Растения с декоративной листвой", "created_at": now, "updated_at": now},
                {"name": "Суккуленты", "description": "Растения, запасающие воду в тканях", "created_at": now, "updated_at": now},
                {"name": "Цветущие", "description": "Растения с красивыми цветами", "created_at": now, "updated_at": now},
                {"name": "Кактусы", "description": "Кактусовые растения", "created_at": now, "updated_at": now},
                {"name": "Папоротники", "description": "Споровые растения", "created_at": now, "updated_at": now},
            ]
            
            categories = []
            for cat_data in categories_data:
                # Создаем каждую категорию отдельно
                result = await session.execute(
                    text("INSERT INTO plant_categories (name, description, created_at, updated_at) VALUES (:name, :description, :created_at, :updated_at) RETURNING id"),
                    {"name": cat_data["name"], "description": cat_data["description"], "created_at": now, "updated_at": now}
                )
                cat_id = result.scalar()
                categories.append({"id": cat_id, **cat_data})
                print(f"✅ Создана категория: {cat_data['name']}")
            
            # 2. Создаем климатические зоны
            zones_data = [
                {"name": "Тропический", "zone_number": 1, "min_temperature": 20, "max_temperature": 35, 
                 "description": "Теплый влажный климат круглый год"},
                {"name": "Субтропический", "zone_number": 2, "min_temperature": 15, "max_temperature": 30, 
                 "description": "Умеренно теплый климат с мягкой зимой"},
                {"name": "Умеренный", "zone_number": 3, "min_temperature": 5, "max_temperature": 25, 
                 "description": "Четыре выраженных сезона"},
                {"name": "Аридный", "zone_number": 5, "min_temperature": -5, "max_temperature": 45, 
                 "description": "Сухой климат с минимумом осадков"},
            ]
            
            climate_zones = []
            for zone_data in zones_data:
                result = await session.execute(
                    text("INSERT INTO climate_zones (name, description, zone_number, min_temperature, max_temperature, created_at, updated_at) VALUES (:name, :description, :zone_number, :min_temperature, :max_temperature, :created_at, :updated_at) RETURNING id"),
                    {
                        "name": zone_data["name"], 
                        "description": zone_data["description"], 
                        "zone_number": zone_data["zone_number"],
                        "min_temperature": zone_data["min_temperature"], 
                        "max_temperature": zone_data["max_temperature"], 
                        "created_at": now, 
                        "updated_at": now
                    }
                )
                zone_id = result.scalar()
                climate_zones.append({"id": zone_id, **zone_data})
                print(f"✅ Создана зона: {zone_data['name']}")
            
            # 3. Создаем теги
            tags_data = [
                {"name": "Для начинающих", "description": "Растения легкие в уходе"},
                {"name": "Популярные", "description": "Самые востребованные растения"},
                {"name": "Очищающие воздух", "description": "Растения, улучшающие качество воздуха"},
                {"name": "Для интерьера", "description": "Идеально подходят для выращивания дома"},
                {"name": "Засухоустойчивые", "description": "Переносят длительные перерывы в поливе"},
            ]
            
            tags = []
            for tag_data in tags_data:
                result = await session.execute(
                    text("INSERT INTO tags (name, description, created_at, updated_at) VALUES (:name, :description, :created_at, :updated_at) RETURNING id"),
                    {"name": tag_data["name"], "description": tag_data["description"], "created_at": now, "updated_at": now}
                )
                tag_id = result.scalar()
                tags.append({"id": tag_id, **tag_data})
                print(f"✅ Создан тег: {tag_data['name']}")
            
            # 4. Создаем растения
            plants_data = [
                {
                    "name": "Монстера Деликатесная",
                    "latin_name": "Monstera deliciosa",
                    "description": "Популярное комнатное растение с характерными разрезными листьями.",
                    "height_min": 150.0,
                    "height_max": 300.0,
                    "growth_rate": "FAST",  # Изменено на верхний регистр
                    "plant_type": "VINE",   # Изменено на верхний регистр
                    "life_cycle": "PERENNIAL",  # Изменено на верхний регистр
                    "popularity_score": 95,
                    "watering_frequency": "WEEKLY",  # Изменено на верхний регистр
                    "light_level": "PARTIAL_SUN",  # Изменено на верхний регистр
                    "temperature_min": 18.0,
                    "temperature_max": 30.0,
                    "humidity_level": "HIGH",  # Изменено на верхний регистр
                    "care_difficulty": "EASY",  # Изменено на верхний регистр
                    "fertilizing_frequency": "MONTHLY",  # Изменено на верхний регистр
                    "repotting_frequency": "BI_ANNUALLY",  # Изменено на верхний регистр
                    "is_toxic": True,
                    "care_instructions": "Монстера любит яркий рассеянный свет, но может переносить полутень. Поливайте, когда верхний слой почвы подсохнет.",
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [1, 2, 3]  # Популярные, Очищающие воздух, Для интерьера
                },
                {
                    "name": "Сансевиерия",
                    "latin_name": "Sansevieria trifasciata",
                    "description": "Неприхотливое растение, известное как 'Тещин язык'.",
                    "height_min": 40.0,
                    "height_max": 120.0,
                    "growth_rate": "SLOW",  # Изменено на верхний регистр
                    "plant_type": "SUCCULENT",  # Изменено на верхний регистр
                    "life_cycle": "PERENNIAL",  # Изменено на верхний регистр
                    "popularity_score": 92,
                    "watering_frequency": "BI_WEEKLY",  # Изменено на верхний регистр
                    "light_level": "SHADE",  # Изменено на верхний регистр
                    "temperature_min": 10.0,
                    "temperature_max": 30.0,
                    "humidity_level": "LOW",  # Изменено на верхний регистр
                    "care_difficulty": "VERY_EASY",  # Изменено на верхний регистр
                    "fertilizing_frequency": "QUARTERLY",  # Изменено на верхний регистр
                    "repotting_frequency": "RARELY",  # Изменено на верхний регистр
                    "is_toxic": True,
                    "care_instructions": "Поливайте только когда почва полностью высохнет. Может расти в условиях низкой освещенности.",
                    "category_ids": [1],  # Суккуленты
                    "climate_zone_ids": [3],  # Аридный
                    "tag_ids": [0, 2, 4]  # Для начинающих, Очищающие воздух, Засухоустойчивые
                },
                {
                    "name": "Замиокулькас",
                    "latin_name": "Zamioculcas zamiifolia",
                    "description": "Неприхотливое растение, известное как 'долларовое дерево'.",
                    "height_min": 45.0,
                    "height_max": 90.0,
                    "growth_rate": "SLOW",  # Изменено на верхний регистр
                    "plant_type": "HERB",  # Изменено на верхний регистр
                    "life_cycle": "PERENNIAL",  # Изменено на верхний регистр
                    "popularity_score": 85,
                    "watering_frequency": "MONTHLY",  # Изменено на верхний регистр
                    "light_level": "LOW_LIGHT",  # Изменено на верхний регистр
                    "temperature_min": 15.0,
                    "temperature_max": 30.0,
                    "humidity_level": "LOW",  # Изменено на верхний регистр
                    "care_difficulty": "VERY_EASY",  # Изменено на верхний регистр
                    "fertilizing_frequency": "QUARTERLY",  # Изменено на верхний регистр
                    "repotting_frequency": "BI_ANNUALLY",  # Изменено на верхний регистр
                    "is_toxic": True,
                    "care_instructions": "Замиокулькас отлично подходит для забывчивых садоводов.",
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [3],  # Аридный
                    "tag_ids": [0, 2, 3, 4]  # Для начинающих, Очищающие воздух, Для интерьера, Засухоустойчивые
                },
                {
                    "name": "Спатифиллум",
                    "latin_name": "Spathiphyllum wallisii",
                    "description": "Изящное цветущее растение, известное как 'Женское счастье'.",
                    "height_min": 40.0,
                    "height_max": 80.0,
                    "growth_rate": "MODERATE",  # Изменено на верхний регистр
                    "plant_type": "FLOWER",  # Изменено на верхний регистр
                    "life_cycle": "PERENNIAL",  # Изменено на верхний регистр
                    "popularity_score": 85,
                    "flowering_period": "Может цвести круглый год при хорошем уходе",
                    "bloom_color": "Белый",
                    "watering_frequency": "WEEKLY",  # Изменено на верхний регистр
                    "light_level": "SHADE",  # Изменено на верхний регистр
                    "temperature_min": 18.0,
                    "temperature_max": 27.0,
                    "humidity_level": "HIGH",  # Изменено на верхний регистр
                    "care_difficulty": "EASY",  # Изменено на верхний регистр
                    "fertilizing_frequency": "MONTHLY",  # Изменено на верхний регистр
                    "repotting_frequency": "ANNUALLY",  # Изменено на верхний регистр
                    "is_toxic": True,
                    "care_instructions": "Спатифиллум предпочитает яркий рассеянный свет и высокую влажность.",
                    "category_ids": [2],  # Цветущие
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [0, 2, 3]  # Для начинающих, Очищающие воздух, Для интерьера
                },
                {
                    "name": "Алоэ Вера",
                    "latin_name": "Aloe vera",
                    "description": "Лекарственное суккулентное растение с мясистыми листьями.",
                    "height_min": 30.0,
                    "height_max": 60.0,
                    "growth_rate": "MODERATE",  # Изменено на верхний регистр
                    "plant_type": "SUCCULENT",  # Изменено на верхний регистр
                    "life_cycle": "PERENNIAL",  # Изменено на верхний регистр
                    "popularity_score": 90,
                    "watering_frequency": "BI_WEEKLY",  # Изменено на верхний регистр
                    "light_level": "FULL_SUN",  # Изменено на верхний регистр
                    "temperature_min": 10.0,
                    "temperature_max": 32.0,
                    "humidity_level": "LOW",  # Изменено на верхний регистр
                    "care_difficulty": "VERY_EASY",  # Изменено на верхний регистр
                    "fertilizing_frequency": "QUARTERLY",  # Изменено на верхний регистр
                    "repotting_frequency": "BI_ANNUALLY",  # Изменено на верхний регистр
                    "is_toxic": False,
                    "care_instructions": "Алоэ вера предпочитает яркий свет и хорошо дренированную почву.",
                    "category_ids": [1],  # Суккуленты
                    "climate_zone_ids": [3],  # Аридный
                    "tag_ids": [0, 4]  # Для начинающих, Засухоустойчивые
                }
            ]
            
            plants = []
            for i, plant_data in enumerate(plants_data):
                # Извлекаем ID связей
                category_ids = plant_data.pop("category_ids", [])
                climate_zone_ids = plant_data.pop("climate_zone_ids", [])
                tag_ids = plant_data.pop("tag_ids", [])
                
                # Подготавливаем данные для вставки
                plant_data["created_at"] = now
                plant_data["updated_at"] = now
                
                # Создаем SQL запрос для вставки растения
                columns = list(plant_data.keys())
                column_names = ", ".join(columns)
                placeholders = ", ".join([f":{col}" for col in columns])
                
                query = f"INSERT INTO plants ({column_names}) VALUES ({placeholders}) RETURNING id"
                result = await session.execute(text(query), plant_data)
                plant_id = result.scalar()
                
                # Добавляем связи с категориями
                for cat_idx in category_ids:
                    if cat_idx < len(categories):
                        await session.execute(
                            text("INSERT INTO plant_category (plant_id, category_id) VALUES (:plant_id, :category_id)"),
                            {"plant_id": plant_id, "category_id": categories[cat_idx]["id"]}
                        )
                
                # Добавляем связи с климатическими зонами
                for zone_idx in climate_zone_ids:
                    if zone_idx < len(climate_zones):
                        await session.execute(
                            text("INSERT INTO plant_climate_zone (plant_id, climate_zone_id) VALUES (:plant_id, :climate_zone_id)"),
                            {"plant_id": plant_id, "climate_zone_id": climate_zones[zone_idx]["id"]}
                        )
                
                # Добавляем связи с тегами
                for tag_idx in tag_ids:
                    if tag_idx < len(tags):
                        await session.execute(
                            text("INSERT INTO plant_tag (plant_id, tag_id) VALUES (:plant_id, :tag_id)"),
                            {"plant_id": plant_id, "tag_id": tags[tag_idx]["id"]}
                        )
                
                plants.append({"id": plant_id, **plant_data})
                print(f"✅ Создано растение {i+1}/{len(plants_data)}: {plant_data['name']}")
            
            # 5. Добавляем изображения
            images_data = [
                # Монстера
                {"plant_id": plants[0]["id"], "url": "/images/plants/monstera-1.jpg", 
                 "alt": "Монстера Деликатесная", "title": "Монстера с разрезными листьями", 
                 "is_primary": True},
                # Сансевиерия
                {"plant_id": plants[1]["id"], "url": "/images/plants/sansevieria-1.jpg", 
                 "alt": "Сансевиерия", "title": "Сансевиерия трёхполосная", 
                 "is_primary": True},
                # Замиокулькас
                {"plant_id": plants[2]["id"], "url": "/images/plants/zamioculcas-1.jpg", 
                 "alt": "Замиокулькас", "title": "Долларовое дерево", 
                 "is_primary": True},
                # Спатифиллум
                {"plant_id": plants[3]["id"], "url": "/images/plants/spathiphyllum-1.jpg", 
                 "alt": "Спатифиллум", "title": "Женское счастье", 
                 "is_primary": True},
                # Алоэ Вера
                {"plant_id": plants[4]["id"], "url": "/images/plants/aloe-vera-1.jpg", 
                 "alt": "Алоэ Вера", "title": "Лечебное алоэ", 
                 "is_primary": True},
            ]
            
            for img_data in images_data:
                await session.execute(
                    text("INSERT INTO plant_images (plant_id, url, alt, title, is_primary, created_at, updated_at) VALUES (:plant_id, :url, :alt, :title, :is_primary, :created_at, :updated_at)"),
                    {
                        "plant_id": img_data["plant_id"], 
                        "url": img_data["url"], 
                        "alt": img_data["alt"],
                        "title": img_data["title"], 
                        "is_primary": img_data["is_primary"], 
                        "created_at": now, 
                        "updated_at": now
                    }
                )
            print(f"✅ Создано {len(images_data)} изображений")
            
            # Сохраняем все изменения
            await session.commit()
            print("\n🎉 Базовые данные успешно добавлены!")
            print(f"📊 Статистика:")
            print(f"  - {len(categories)} категорий")
            print(f"  - {len(climate_zones)} климатических зон")
            print(f"  - {len(tags)} тегов")
            print(f"  - {len(plants)} растений")
            print(f"  - {len(images_data)} изображений")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при добавлении данных: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await session.close()
            break


if __name__ == "__main__":
    asyncio.run(seed_basic_plants_data())