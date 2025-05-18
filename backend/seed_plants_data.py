# backend/seed_plants_data.py

import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.domain.models.plant_category import PlantCategory
from app.domain.models.climate_zone import ClimateZone
from app.domain.models.tag import Tag
from app.domain.models.plant import Plant
from app.domain.models.plant_image import PlantImage

async def seed_full_plants_data():
    """Добавляем полные данные для растений с примерами"""
    async for session in get_db():
        try:
            # 1. Создаем категории растений
            categories_data = [
                {"name": "Лиственные", "description": "Растения с декоративной листвой"},
                {"name": "Суккуленты", "description": "Растения, запасающие воду в тканях"},
                {"name": "Цветущие", "description": "Растения с красивыми цветами"},
                {"name": "Кактусы", "description": "Кактусовые растения"},
                {"name": "Папоротники", "description": "Споровые растения"},
                {"name": "Пальмы", "description": "Пальмовые растения"},
                {"name": "Орхидеи", "description": "Эпифитные цветущие растения"},
            ]
            
            categories = []
            for cat_data in categories_data:
                category = PlantCategory(**cat_data)
                session.add(category)
                categories.append(category)
            
            await session.flush()  # Получаем ID категорий
            
            # 2. Создаем климатические зоны
            zones_data = [
                {"name": "Тропический", "zone_number": 1, "min_temperature": 20, "max_temperature": 35, 
                 "description": "Теплый влажный климат круглый год"},
                {"name": "Субтропический", "zone_number": 2, "min_temperature": 15, "max_temperature": 30, 
                 "description": "Умеренно теплый климат с мягкой зимой"},
                {"name": "Умеренный", "zone_number": 3, "min_temperature": 5, "max_temperature": 25, 
                 "description": "Четыре выраженных сезона"},
                {"name": "Континентальный", "zone_number": 4, "min_temperature": -10, "max_temperature": 30, 
                 "description": "Резкие перепады температур"},
                {"name": "Аридный", "zone_number": 5, "min_temperature": -5, "max_temperature": 45, 
                 "description": "Сухой климат с минимумом осадков"},
                {"name": "Средиземноморский", "zone_number": 6, "min_temperature": 10, "max_temperature": 30, 
                 "description": "Мягкая дождливая зима, сухое жаркое лето"},
            ]
            
            climate_zones = []
            for zone_data in zones_data:
                zone = ClimateZone(**zone_data)
                session.add(zone)
                climate_zones.append(zone)
            
            await session.flush()  # Получаем ID зон
            
            # 3. Создаем теги
            tags_data = [
                {"name": "Для начинающих", "description": "Растения легкие в уходе"},
                {"name": "Популярные", "description": "Самые востребованные растения"},
                {"name": "Очищающие воздух", "description": "Растения, улучшающие качество воздуха"},
                {"name": "Тропические", "description": "Растения из тропических регионов"},
                {"name": "Теневыносливые", "description": "Растения, растущие в условиях слабого освещения"},
                {"name": "Для интерьера", "description": "Идеально подходят для выращивания дома"},
                {"name": "Засухоустойчивые", "description": "Переносят длительные перерывы в поливе"},
                {"name": "Быстрорастущие", "description": "Растения с высокой скоростью роста"},
            ]
            
            tags = []
            for tag_data in tags_data:
                tag = Tag(**tag_data)
                session.add(tag)
                tags.append(tag)
            
            await session.flush()  # Получаем ID тегов
            
            # 4. Создаем растения с полной информацией
            plants_data = [
                {
                    "name": "Монстера Деликатесная",
                    "latin_name": "Monstera deliciosa",
                    "description": "Популярное комнатное растение с характерными разрезными листьями. Монстера относится к семейству Ароидных и получила свое название за съедобные плоды. В природе встречается в тропических лесах Центральной Америки.",
                    "height_min": 150.0,
                    "height_max": 300.0,
                    "growth_rate": "fast",
                    "plant_type": "vine",
                    "life_cycle": "perennial",
                    "popularity_score": 95,
                    "flowering_period": "Редко цветет в домашних условиях",
                    "bloom_color": "Кремово-белый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 18.0,
                    "temperature_max": 30.0,
                    "humidity_level": "high",
                    "care_difficulty": "easy",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": True,
                    "care_instructions": "Монстера любит яркий рассеянный свет, но может переносить полутень. Поливайте, когда верхний слой почвы подсохнет. В период активного роста (весна-лето) подкармливайте раз в месяц. Протирайте листья влажной тряпкой для удаления пыли. Обеспечьте опору для роста.",
                    "planting_instructions": "Используйте рыхлую почвенную смесь с хорошим дренажем. Идеальный состав: 1 часть садовой земли, 1 часть перегноя, 1 часть песка и 1 часть торфа. Выберите горшок достаточно большой, чтобы вместить корневую систему и опору для растения.",
                    "pruning_tips": "Обрезайте пожелтевшие или поврежденные листья. Можно прищипывать верхушку для стимуляции ветвления. Обрезку лучше проводить весной.",
                    "notes": "Сок растения может вызывать раздражение кожи, поэтому используйте перчатки при обрезке. Воздушные корни можно направлять к опоре или обрезать.",
                    "care_tips": json.dumps([
                        "Размещайте вдали от прямых солнечных лучей",
                        "Увеличьте влажность с помощью опрыскивания",
                        "Используйте мох на опоре для воздушных корней",
                        "Поворачивайте горшок для равномерного роста"
                    ]),
                    "common_problems": json.dumps([
                        {
                            "title": "Желтеющие листья",
                            "description": "Листья монстеры могут желтеть из-за избыточного полива, недостатка света или питательных веществ.",
                            "solution": "Проверьте режим полива, убедитесь что растение получает достаточно света. Подкормите универсальным удобрением."
                        },
                        {
                            "title": "Отсутствие разрезов на листьях",
                            "description": "Молодые или получающие недостаточно света растения могут не формировать характерные разрезы.",
                            "solution": "Увеличьте освещение и будьте терпеливы, с возрастом листья станут более разрезными."
                        }
                    ]),
                    "propagation_methods": json.dumps([
                        {
                            "name": "Черенкование",
                            "description": "Отрежьте часть стебля с листом и воздушным корнем. Поставьте в воду или высадите в легкую почву.",
                            "difficulty": 2
                        },
                        {
                            "name": "Деление куста",
                            "description": "При пересадке разделите растение на части, убедившись что у каждой есть корни.",
                            "difficulty": 3
                        }
                    ]),
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [1, 2, 5]  # Популярные, Очищающие воздух, Для интерьера
                },
                {
                    "name": "Фикус Лирата",
                    "latin_name": "Ficus lyrata",
                    "description": "Популярное комнатное растение с большими скрипичными листьями. Фикус лирата относится к семейству Тутовых и родом из тропических лесов Западной Африки. Его крупные, глянцевые листья делают его отличным акцентом в интерьере.",
                    "height_min": 180.0,
                    "height_max": 300.0,
                    "growth_rate": "moderate",
                    "plant_type": "tree",
                    "life_cycle": "perennial",
                    "popularity_score": 88,
                    "flowering_period": "Обычно не цветет в домашних условиях",
                    "hardiness_zone_min": 10,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 16.0,
                    "temperature_max": 28.0,
                    "humidity_level": "medium",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "bi_weekly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": True,
                    "care_instructions": "Фикус лирата предпочитает яркий непрямой свет. Поливайте когда верхний слой почвы (2-3 см) полностью высохнет. Избегайте сквозняков и резких перепадов температуры. Листья нуждаются в регулярной очистке от пыли.",
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [1, 5]  # Популярные, Для интерьера
                },
                {
                    "name": "Сансевиерия",
                    "latin_name": "Sansevieria trifasciata",
                    "description": "Неприхотливое растение, известное своей способностью очищать воздух. Сансевиерия, или 'Тещин язык', относится к семейству Спаржевых. Родом из засушливых регионов Западной Африки, отлично адаптирована к сухим условиям.",
                    "height_min": 40.0,
                    "height_max": 120.0,
                    "growth_rate": "slow",
                    "plant_type": "succulent",
                    "life_cycle": "perennial",
                    "popularity_score": 92,
                    "flowering_period": "Редко цветет весной или летом",
                    "bloom_color": "Белый или кремовый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "bi_weekly",
                    "light_level": "shade",
                    "temperature_min": 10.0,
                    "temperature_max": 30.0,
                    "humidity_level": "low",
                    "care_difficulty": "very_easy",
                    "fertilizing_frequency": "quarterly",
                    "repotting_frequency": "rarely",
                    "is_toxic": True,
                    "care_instructions": "Сансевиерия - одно из самых неприхотливых растений. Поливайте только когда почва полностью высохнет. Может расти в условиях низкой освещенности. Подкармливайте раз в квартал в период роста.",
                    "care_tips": json.dumps([
                        "Лучше недополить, чем перелить",
                        "Идеально для спален - выделяет кислород ночью",
                        "Протирайте листья для поддержания блеска"
                    ]),
                    "category_ids": [1],  # Суккуленты
                    "climate_zone_ids": [4, 3],  # Аридный, Умеренный
                    "tag_ids": [0, 2, 6]  # Для начинающих, Очищающие воздух, Засухоустойчивые
                },
                {
                    "name": "Замиокулькас",
                    "latin_name": "Zamioculcas zamiifolia",
                    "description": "Неприхотливое растение с глянцевыми темно-зелеными листьями. Замиокулькас, также известный как 'долларовое дерево', родом из Восточной Африки. Это суккулентное растение с толстыми стеблями и клубневидными корнями.",
                    "height_min": 45.0,
                    "height_max": 90.0,
                    "growth_rate": "slow",
                    "plant_type": "herb",
                    "life_cycle": "perennial",
                    "popularity_score": 85,
                    "flowering_period": "Редко цветет в домашних условиях",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "monthly",
                    "light_level": "low_light",
                    "temperature_min": 15.0,
                    "temperature_max": 30.0,
                    "humidity_level": "low",
                    "care_difficulty": "very_easy",
                    "fertilizing_frequency": "quarterly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": True,
                    "care_instructions": "Замиокулькас отлично подходит для забывчивых садоводов. Поливайте только когда почва полностью высохнет, обычно раз в 3-4 недели. Может расти в условиях низкой освещенности.",
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [4],  # Аридный
                    "tag_ids": [0, 2, 4, 6]  # Для начинающих, Очищающие воздух, Теневыносливые, Засухоустойчивые
                },
                {
                    "name": "Орхидея Фаленопсис",
                    "latin_name": "Phalaenopsis spp.",
                    "description": "Популярная комнатная орхидея, известная как 'орхидея-бабочка'. Фаленопсис - эпифитное растение родом из тропической Азии. В природе растет на деревьях, получая питательные вещества из воздуха и дождя.",
                    "height_min": 30.0,
                    "height_max": 60.0,
                    "growth_rate": "slow",
                    "plant_type": "flower",
                    "life_cycle": "perennial",
                    "popularity_score": 78,
                    "flowering_period": "Может цвести несколько месяцев, зимой или весной",
                    "bloom_color": "Белый, розовый, фиолетовый, желтый",
                    "hardiness_zone_min": 10,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 18.0,
                    "temperature_max": 29.0,
                    "humidity_level": "high",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "bi_weekly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": False,
                    "care_instructions": "Фаленопсис предпочитает яркий рассеянный свет. Поливайте методом погружения раз в неделю. Используйте специальный субстрат для орхидей. Удобряйте специальным удобрением для орхидей.",
                    "care_tips": json.dumps([
                        "Не допускайте застоя воды в пазухах листьев",
                        "Повышайте влажность с помощью поддона с галькой",
                        "После цветения не обрезайте зеленый цветонос"
                    ]),
                    "category_ids": [2, 6],  # Цветущие, Орхидеи
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [1, 3]  # Популярные, Тропические
                }
            ]
            
            plants = []
            for plant_data in plants_data:
                # Извлекаем ID связей
                category_ids = plant_data.pop("category_ids", [])
                climate_zone_ids = plant_data.pop("climate_zone_ids", [])
                tag_ids = plant_data.pop("tag_ids", [])
                
                # Создаем растение
                plant = Plant(**plant_data)
                session.add(plant)
                
                # Добавляем связи с категориями
                for cat_idx in category_ids:
                    if cat_idx < len(categories):
                        plant.categories.append(categories[cat_idx])
                
                # Добавляем связи с климатическими зонами
                for zone_idx in climate_zone_ids:
                    if zone_idx < len(climate_zones):
                        plant.climate_zones.append(climate_zones[zone_idx])
                
                # Добавляем связи с тегами
                for tag_idx in tag_ids:
                    if tag_idx < len(tags):
                        plant.tags.append(tags[tag_idx])
                
                plants.append(plant)
            
            await session.flush()  # Получаем ID растений
            
            # 5. Добавляем изображения для растений
            images_data = [
                # Монстера
                {"plant_id": plants[0].id, "url": "/images/plants/monstera-1.jpg", 
                 "alt": "Монстера Деликатесная", "title": "Монстера с разрезными листьями", 
                 "is_primary": True},
                {"plant_id": plants[0].id, "url": "/images/plants/monstera-2.jpg", 
                 "alt": "Лист монстеры крупным планом", "title": "Детальный вид листа"},
                
                # Фикус Лирата
                {"plant_id": plants[1].id, "url": "/images/plants/ficus-lyrata-1.jpg", 
                 "alt": "Фикус Лирата", "title": "Фикус со скрипичными листьями", 
                 "is_primary": True},
                
                # Сансевиерия
                {"plant_id": plants[2].id, "url": "/images/plants/sansevieria-1.jpg", 
                 "alt": "Сансевиерия", "title": "Сансевиерия трёхполосная", 
                 "is_primary": True},
                
                # Замиокулькас
                {"plant_id": plants[3].id, "url": "/images/plants/zamioculcas-1.jpg", 
                 "alt": "Замиокулькас", "title": "Долларовое дерево", 
                 "is_primary": True},
                
                # Орхидея
                {"plant_id": plants[4].id, "url": "/images/plants/phalaenopsis-1.jpg", 
                 "alt": "Орхидея Фаленопсис", "title": "Цветущий Фаленопсис", 
                 "is_primary": True},
                {"plant_id": plants[4].id, "url": "/images/plants/phalaenopsis-2.jpg", 
                 "alt": "Цветы орхидеи", "title": "Цветы крупным планом"},
            ]
            
            for img_data in images_data:
                image = PlantImage(**img_data)
                session.add(image)
            
            # Сохраняем все изменения
            await session.commit()
            print("✅ Полные данные для растений успешно добавлены!")
            print(f"Создано:")
            print(f"  - {len(categories)} категорий")
            print(f"  - {len(climate_zones)} климатических зон")
            print(f"  - {len(tags)} тегов")
            print(f"  - {len(plants)} растений")
            print(f"  - {len(images_data)} изображений")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при добавлении данных: {e}")
            raise
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(seed_full_plants_data())