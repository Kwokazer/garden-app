import asyncio
import json
import sys
import os

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


async def seed_plants_data():
    """Добавляем расширенные данные для растений"""
    async for session in get_db():
        try:
            print("🌱 Начинаем заполнение базы данных растений...")
            
            # Загружаем все модели для правильной работы migrations
            from app.domain.models.base import Base
            from app.domain.models.plant import Plant
            from app.domain.models.plant_category import PlantCategory
            from app.domain.models.climate_zone import ClimateZone
            from app.domain.models.tag import Tag
            from app.domain.models.plant_image import PlantImage
            
            # 1. Создаем категории растений (по одной за раз для правильной работы timestamps)
            categories_data = [
                {"name": "Лиственные", "description": "Растения с декоративной листвой"},
                {"name": "Суккуленты", "description": "Растения, запасающие воду в тканях"},
                {"name": "Цветущие", "description": "Растения с красивыми цветами"},
                {"name": "Кактусы", "description": "Кактусовые растения"},
                {"name": "Папоротники", "description": "Споровые растения"},
                {"name": "Пальмы", "description": "Пальмовые растения"},
                {"name": "Орхидеи", "description": "Эпифитные цветущие растения"},
                {"name": "Овощные", "description": "Съедобные овощные культуры"},
                {"name": "Плодовые", "description": "Плодоносящие растения"},
                {"name": "Травы и специи", "description": "Ароматические и кулинарные травы"},
                {"name": "Вьющиеся", "description": "Лианы и вьющиеся растения"},
                {"name": "Водные", "description": "Аквариумные и болотные растения"},
            ]
            
            categories = []
            for cat_data in categories_data:
                category = PlantCategory(**cat_data)
                session.add(category)
                await session.flush()  # Фиксируем каждую категорию отдельно
                categories.append(category)
            print(f"✅ Создано {len(categories)} категорий")
            
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
                {"name": "Арктический", "zone_number": 7, "min_temperature": -25, "max_temperature": 15, 
                 "description": "Холодный климат с коротким летом"},
            ]
            
            climate_zones = []
            for zone_data in zones_data:
                zone = ClimateZone(**zone_data)
                session.add(zone)
                await session.flush()  # Фиксируем каждую зону отдельно
                climate_zones.append(zone)
            print(f"✅ Создано {len(climate_zones)} климатических зон")
            
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
                {"name": "Съедобные", "description": "Съедобные части растения"},
                {"name": "Лечебные", "description": "Растения с лечебными свойствами"},
                {"name": "Ароматные", "description": "Источают приятный аромат"},
                {"name": "Для балкона", "description": "Подходят для выращивания на балконе"},
                {"name": "Морозостойкие", "description": "Переносят отрицательные температуры"},
                {"name": "Влаголюбивые", "description": "Требуют обильного полива"},
                {"name": "Эпифиты", "description": "Растения, растущие на других растениях"},
                {"name": "Коллекционные", "description": "Редкие и необычные виды"},
            ]
            
            tags = []
            for tag_data in tags_data:
                tag = Tag(**tag_data)
                session.add(tag)
                await session.flush()  # Фиксируем каждый тег отдельно
                tags.append(tag)
            print(f"✅ Создано {len(tags)} тегов")
            
            # 4. Создаем растения с полной информацией
            plants_data = [
                # Лиственные комнатные растения
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
                    "category_ids": [0, 10],  # Лиственные, Вьющиеся
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [1, 2, 5, 3]  # Популярные, Очищающие воздух, Для интерьера, Тропические
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
                    "care_tips": json.dumps([
                        "Поворачивайте растение каждую неделю для равномерного роста",
                        "Протирайте листья влажной тряпкой раз в неделю",
                        "Избегайте частых перестановок",
                        "Обеспечьте хорошее освещение без прямых лучей"
                    ]),
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [1, 5]  # Популярные, Для интерьера
                },
                
                # Суккуленты
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
                        "Протирайте листья для поддержания блеска",
                        "Может расти при искусственном освещении"
                    ]),
                    "category_ids": [1],  # Суккуленты
                    "climate_zone_ids": [4, 3],  # Аридный, Умеренный
                    "tag_ids": [0, 2, 6, 5]  # Для начинающих, Очищающие воздух, Засухоустойчивые, Для интерьера
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
                    "care_tips": json.dumps([
                        "Идеален для темных углов",
                        "Переносит забывчивых хозяев",
                        "Хорошо растет при искусственном освещении",
                        "Листья можно протирать влажной тряпкой"
                    ]),
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [4],  # Аридный
                    "tag_ids": [0, 2, 4, 6, 5]  # Для начинающих, Очищающие воздух, Теневыносливые, Засухоустойчивые, Для интерьера
                },
                
                # Орхидеи
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
                        "После цветения не обрезайте зеленый цветонос",
                        "Поливайте только корни, избегая попадания воды на листья"
                    ]),
                    "category_ids": [2, 6],  # Цветущие, Орхидеи
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [1, 3, 14, 15]  # Популярные, Тропические, Эпифиты, Коллекционные
                },
                
                # Папоротники
                {
                    "name": "Нефролепис",
                    "latin_name": "Nephrolepis exaltata",
                    "description": "Популярный комнатный папоротник с изящными перистыми листьями. Нефролепис - один из самых выносливых папоротников для домашнего выращивания. Родом из тропических и субтропических регионов мира.",
                    "height_min": 30.0,
                    "height_max": 90.0,
                    "growth_rate": "moderate",
                    "plant_type": "fern",
                    "life_cycle": "perennial",
                    "popularity_score": 72,
                    "flowering_period": "Папоротники не цветут",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "bi_weekly",
                    "light_level": "shade",
                    "temperature_min": 16.0,
                    "temperature_max": 24.0,
                    "humidity_level": "high",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "annually",
                    "is_toxic": False,
                    "care_instructions": "Нефролепис предпочитает высокую влажность и рассеянный свет. Почва должна быть всегда слегка влажной, но не переувлажненной. Регулярно опрыскивайте листья.",
                    "care_tips": json.dumps([
                        "Увеличивайте влажность воздуха любыми способами",
                        "Удаляйте засохшие листья у основания",
                        "Держите подальше от батарей отопления",
                        "Летом выносите на свежий воздух в тень"
                    ]),
                    "category_ids": [4],  # Папоротники
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [2, 4, 5, 13]  # Очищающие воздух, Теневыносливые, Для интерьера, Влаголюбивые
                },
                
                # Пальмы
                {
                    "name": "Хамедорея изящная",
                    "latin_name": "Chamaedorea elegans",
                    "description": "Элегантная комнатная пальма, также известная как 'горная пальма'. Хамедорея - одна из самых популярных комнатных пальм благодаря своей неприхотливости и изящному внешнему виду. Родом из Мексики и Центральной Америки.",
                    "height_min": 90.0,
                    "height_max": 200.0,
                    "growth_rate": "slow",
                    "plant_type": "tree",
                    "life_cycle": "perennial",
                    "popularity_score": 75,
                    "flowering_period": "Может цвести весной мелкими желтыми цветками",
                    "bloom_color": "Желтый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 18.0,
                    "temperature_max": 27.0,
                    "humidity_level": "medium",
                    "care_difficulty": "easy",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": False,
                    "care_instructions": "Хамедорея предпочитает яркий рассеянный свет, но переносит полутень. Поливайте регулярно, не допуская пересыхания почвы. Опрыскивайте листья в сухую погоду.",
                    "care_tips": json.dumps([
                        "Протирайте листья влажной губкой",
                        "Удаляйте засохшие листья",
                        "Поворачивайте горшок для равномерного роста",
                        "Летом можно выносить на балкон в тень"
                    ]),
                    "category_ids": [5],  # Пальмы
                    "climate_zone_ids": [0, 1],  # Тропический, Субтропический
                    "tag_ids": [0, 2, 5, 11]  # Для начинающих, Очищающие воздух, Для интерьера, Для балкона
                },
                
                # Овощные культуры
                {
                    "name": "Базилик",
                    "latin_name": "Ocimum basilicum",
                    "description": "Ароматная пряная трава семейства яснотковых. Базилик - одна из самых популярных кулинарных трав, широко используется в итальянской и средиземноморской кухне. Легко выращивается в домашних условиях.",
                    "height_min": 20.0,
                    "height_max": 60.0,
                    "growth_rate": "fast",
                    "plant_type": "herb",
                    "life_cycle": "annual",
                    "popularity_score": 85,
                    "flowering_period": "Лето, но цветки лучше удалять",
                    "bloom_color": "Белый, розовый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "twice_a_week",
                    "light_level": "full_sun",
                    "temperature_min": 15.0,
                    "temperature_max": 30.0,
                    "humidity_level": "medium",
                    "care_difficulty": "easy",
                    "fertilizing_frequency": "bi_weekly",
                    "repotting_frequency": "annually",
                    "is_toxic": False,
                    "care_instructions": "Базилик любит тепло и яркий свет. Поливайте регулярно, не допуская пересыхания почвы. Прищипывайте цветоносы для лучшего роста листьев. Собирайте листья регулярно.",
                    "care_tips": json.dumps([
                        "Прищипывайте цветки для лучшего вкуса листьев",
                        "Собирайте листья утром после испарения росы",
                        "Можно выращивать на подоконнике круглый год",
                        "Регулярная обрезка стимулирует рост"
                    ]),
                    "category_ids": [9, 7],  # Травы и специи, Овощные
                    "climate_zone_ids": [1, 5],  # Субтропический, Средиземноморский
                    "tag_ids": [0, 8, 10, 7, 11]  # Для начинающих, Съедобные, Ароматные, Быстрорастущие, Для балкона
                },
                {
                    "name": "Томат Черри",
                    "latin_name": "Solanum lycopersicum var. cerasiforme",
                    "description": "Мелкоплодный томат, идеально подходящий для домашнего выращивания. Томаты черри дают обильный урожай сладких мелких плодов. Можно выращивать в горшках на балконе или подоконнике.",
                    "height_min": 30.0,
                    "height_max": 150.0,
                    "growth_rate": "fast",
                    "plant_type": "vegetable",
                    "life_cycle": "annual",
                    "popularity_score": 80,
                    "flowering_period": "Июнь-сентябрь",
                    "bloom_color": "Желтый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "twice_a_week",
                    "light_level": "full_sun",
                    "temperature_min": 15.0,
                    "temperature_max": 30.0,
                    "humidity_level": "medium",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "weekly",
                    "repotting_frequency": "annually",
                    "is_toxic": False,
                    "care_instructions": "Томаты черри требуют много света и тепла. Поливайте регулярно, но избегайте переувлажнения. Подкармливайте еженедельно в период плодоношения. Подвязывайте растения к опоре.",
                    "care_tips": json.dumps([
                        "Нуждается в опоре по мере роста",
                        "Удаляйте нижние листья для лучшей вентиляции",
                        "Прищипывайте пасынки для лучшего плодоношения",
                        "Поливайте под корень, избегая попадания на листья"
                    ]),
                    "category_ids": [7],  # Овощные
                    "climate_zone_ids": [1, 2, 5],  # Субтропический, Умеренный, Средиземноморский
                    "tag_ids": [8, 7, 11, 13]  # Съедобные, Быстрорастущие, Для балкона, Влаголюбивые
                },
                
                # Плодовые
                {
                    "name": "Лимон Мейера",
                    "latin_name": "Citrus × meyeri",
                    "description": "Компактный цитрус, идеальный для домашнего выращивания. Лимон Мейера - гибрид лимона и мандарина, дающий сладкие, менее кислые плоды. Может плодоносить в горшечной культуре.",
                    "height_min": 100.0,
                    "height_max": 180.0,
                    "growth_rate": "moderate",
                    "plant_type": "fruit",
                    "life_cycle": "perennial",
                    "popularity_score": 70,
                    "flowering_period": "Весна-лето, может цвести круглый год",
                    "bloom_color": "Белый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "weekly",
                    "light_level": "full_sun",
                    "temperature_min": 10.0,
                    "temperature_max": 30.0,
                    "humidity_level": "medium",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": False,
                    "care_instructions": "Лимон нуждается в ярком освещении минимум 8 часов в день. Поливайте когда верхний слой почвы подсохнет. Зимой содержите в прохладе (10-15°C). Регулярно подкармливайте удобрением для цитрусов.",
                    "care_tips": json.dumps([
                        "Зимой нуждается в прохладном содержании",
                        "Может потребоваться дополнительное освещение",
                        "Регулярно проветривайте помещение",
                        "Летом выносите на улицу"
                    ]),
                    "category_ids": [8],  # Плодовые
                    "climate_zone_ids": [1, 5],  # Субтропический, Средиземноморский
                    "tag_ids": [8, 10, 11, 15]  # Съедобные, Ароматные, Для балкона, Коллекционные
                },
                
                # Кактусы
                {
                    "name": "Эхинокактус Грузони",
                    "latin_name": "Echinocactus grusonii",
                    "description": "Популярный шаровидный кактус, известный как 'Золотая бочка'. Эхинокактус Грузони - один из самых узнаваемых кактусов с выраженными ребрами и золотистыми колючками. Родом из Мексики.",
                    "height_min": 15.0,
                    "height_max": 60.0,
                    "growth_rate": "slow",
                    "plant_type": "succulent",
                    "life_cycle": "perennial",
                    "popularity_score": 65,
                    "flowering_period": "Цветет только в зрелом возрасте летом",
                    "bloom_color": "Желтый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "monthly",
                    "light_level": "full_sun",
                    "temperature_min": 10.0,
                    "temperature_max": 35.0,
                    "humidity_level": "low",
                    "care_difficulty": "very_easy",
                    "fertilizing_frequency": "quarterly",
                    "repotting_frequency": "rarely",
                    "is_toxic": False,
                    "care_instructions": "Эхинокактус очень неприхотлив. Нуждается в ярком солнечном свете. Поливайте редко, только когда почва полностью высохнет. Зимой полив практически прекращают.",
                    "care_tips": json.dumps([
                        "Зимой содержите в прохладе и практически без полива",
                        "Обеспечьте максимум солнечного света",
                        "Используйте хорошо дренированную почву для кактусов",
                        "Будьте осторожны с острыми колючками"
                    ]),
                    "category_ids": [3, 1],  # Кактусы, Суккуленты
                    "climate_zone_ids": [4],  # Аридный
                    "tag_ids": [0, 6, 5]  # Для начинающих, Засухоустойчивые, Для интерьера
                },
                
                # Водные растения
                {
                    "name": "Анубиас Нана",
                    "latin_name": "Anubias barteri var. nana",
                    "description": "Популярное аквариумное растение с темно-зелеными кожистыми листьями. Анубиас нана - выносливое растение, подходящее для начинающих аквариумистов. Может расти как полностью погруженным, так и частично над водой.",
                    "height_min": 5.0,
                    "height_max": 15.0,
                    "growth_rate": "slow",
                    "plant_type": "aquatic",
                    "life_cycle": "perennial",
                    "popularity_score": 78,
                    "flowering_period": "Может цвести белым цветком над водой",
                    "bloom_color": "Белый",
                    "hardiness_zone_min": 10,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "daily",  # всегда в воде
                    "light_level": "low_light",
                    "temperature_min": 22.0,
                    "temperature_max": 28.0,
                    "humidity_level": "high",  # всегда влажно
                    "care_difficulty": "easy",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "rarely",
                    "is_toxic": False,
                    "care_instructions": "Анубиас хорошо растет при слабом освещении. Не закапывайте корневище в грунт - привязывайте к корягам или камням. Подкармливайте жидкими удобрениями для аквариумных растений.",
                    "care_tips": json.dumps([
                        "Привязывайте к декорациям, не сажайте в грунт",
                        "Хорошо переносит слабое освещение",
                        "Удаляйте старые поврежденные листья",
                        "Подходит для аквариумов любого размера"
                    ]),
                    "category_ids": [11],  # Водные
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [0, 4, 3]  # Для начинающих, Теневыносливые, Тропические
                },
                
                # Лекарственные травы
                {
                    "name": "Алоэ Вера",
                    "latin_name": "Aloe vera",
                    "description": "Лекарственное суккулентное растение с мясистыми листьями. Алоэ вера известно своими целебными свойствами и широко используется в косметике и народной медицине. Очень неприхотливо в уходе.",
                    "height_min": 30.0,
                    "height_max": 60.0,
                    "growth_rate": "moderate",
                    "plant_type": "succulent",
                    "life_cycle": "perennial",
                    "popularity_score": 90,
                    "flowering_period": "Редко цветет зимой или весной",
                    "bloom_color": "Оранжевый, красный",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "bi_weekly",
                    "light_level": "full_sun",
                    "temperature_min": 10.0,
                    "temperature_max": 32.0,
                    "humidity_level": "low",
                    "care_difficulty": "very_easy",
                    "fertilizing_frequency": "quarterly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": False,
                    "care_instructions": "Алоэ вера предпочитает яркий свет и хорошо дренированную почву. Поливайте умеренно, давая почве полностью просохнуть между поливами. Зимой полив сократите.",
                    "care_tips": json.dumps([
                        "Сок листьев можно использовать для лечения ожогов",
                        "Срезайте внешние зрелые листья для использования",
                        "Дает много деток, которые можно пересаживать",
                        "Летом может расти на открытом воздухе"
                    ]),
                    "category_ids": [1],  # Суккуленты
                    "climate_zone_ids": [4, 5],  # Аридный, Средиземноморский
                    "tag_ids": [0, 9, 6, 11]  # Для начинающих, Лечебные, Засухоустойчивые, Для балкона
                },
                
                # Ампельные растения
                {
                    "name": "Хлорофитум хохлатый",
                    "latin_name": "Chlorophytum comosum",
                    "description": "Популярное ампельное растение с длинными узкими листьями и характерными детками на столонах. Хлорофитум - одно из лучших растений для очистки воздуха. Родом из Южной Африки.",
                    "height_min": 20.0,
                    "height_max": 40.0,
                    "growth_rate": "fast",
                    "plant_type": "herb",
                    "life_cycle": "perennial",
                    "popularity_score": 88,
                    "flowering_period": "Лето, мелкие белые цветки",
                    "bloom_color": "Белый",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 15.0,
                    "temperature_max": 25.0,
                    "humidity_level": "medium",
                    "care_difficulty": "very_easy",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "annually",
                    "is_toxic": False,
                    "care_instructions": "Хлорофитум очень неприхотлив. Предпочитает яркий рассеянный свет, но переносит полутень. Поливайте регулярно в период роста. Легко размножается детками.",
                    "care_tips": json.dumps([
                        "Прекрасно смотрится в подвесных кашпо",
                        "Детки можно укоренять, не отделяя от материнского растения",
                        "Хорошо очищает воздух от формальдегида",
                        "Переносит кратковременную засуху"
                    ]),
                    "propagation_methods": json.dumps([
                        {
                            "name": "Детками",
                            "description": "Укореняйте детки в воде или сразу в почве, не отделяя от материнского растения",
                            "difficulty": 1
                        },
                        {
                            "name": "Делением куста",
                            "description": "При пересадке разделите разросшийся куст на части",
                            "difficulty": 2
                        }
                    ]),
                    "category_ids": [0],  # Лиственные
                    "climate_zone_ids": [1, 2],  # Субтропический, Умеренный
                    "tag_ids": [0, 2, 7, 5]  # Для начинающих, Очищающие воздух, Быстрорастущие, Для интерьера
                },
                
                # Цветущие растения
                {
                    "name": "Спатифиллум",
                    "latin_name": "Spathiphyllum wallisii",
                    "description": "Изящное цветущее растение, известное как 'Женское счастье'. Спатифиллум ценится за красивые белые цветы-покрывала и темно-зеленые листья. Отличное растение для очистки воздуха.",
                    "height_min": 40.0,
                    "height_max": 80.0,
                    "growth_rate": "moderate",
                    "plant_type": "flower",
                    "life_cycle": "perennial",
                    "popularity_score": 85,
                    "flowering_period": "Может цвести круглый год при хорошем уходе",
                    "bloom_color": "Белый",
                    "hardiness_zone_min": 10,
                    "hardiness_zone_max": 12,
                    "watering_frequency": "weekly",
                    "light_level": "shade",
                    "temperature_min": 18.0,
                    "temperature_max": 27.0,
                    "humidity_level": "high",
                    "care_difficulty": "easy",
                    "fertilizing_frequency": "monthly",
                    "repotting_frequency": "annually",
                    "is_toxic": True,
                    "care_instructions": "Спатифиллум предпочитает яркий рассеянный свет и высокую влажность. Поливайте регулярно, не допуская пересыхания почвы. Опрыскивайте листья, избегая попадания воды на цветы.",
                    "care_tips": json.dumps([
                        "Увядающие листья сигнализируют о необходимости полива",
                        "Удаляйте отцветшие цветоносы для стимуляции нового цветения",
                        "Повышайте влажность опрыскиванием или поддоном с водой",
                        "Может расти при искусственном освещении"
                    ]),
                    "category_ids": [2],  # Цветущие
                    "climate_zone_ids": [0],  # Тропический
                    "tag_ids": [0, 2, 4, 5, 13]  # Для начинающих, Очищающие воздух, Теневыносливые, Для интерьера, Влаголюбивые
                },
                
                # Хвойные
                {
                    "name": "Норфолкская сосна",
                    "latin_name": "Araucaria heterophylla",
                    "description": "Комнатная хвойная елка, популярная как живая новогодняя елка. Норфолкская сосна - медленнорастущее дерево с симметричной кроной и мягкой хвоей. Родом с острова Норфолк.",
                    "height_min": 100.0,
                    "height_max": 200.0,
                    "growth_rate": "slow",
                    "plant_type": "tree",
                    "life_cycle": "perennial",
                    "popularity_score": 60,
                    "flowering_period": "Не цветет в домашних условиях",
                    "hardiness_zone_min": 9,
                    "hardiness_zone_max": 11,
                    "watering_frequency": "weekly",
                    "light_level": "partial_sun",
                    "temperature_min": 16.0,
                    "temperature_max": 24.0,
                    "humidity_level": "medium",
                    "care_difficulty": "moderate",
                    "fertilizing_frequency": "quarterly",
                    "repotting_frequency": "bi_annually",
                    "is_toxic": False,
                    "care_instructions": "Норфолкская сосна нуждается в прохладном содержании и высокой влажности. Избегайте пересыхания почвы и резких перепадов температуры. Регулярно поворачивайте для равномерного роста.",
                    "care_tips": json.dumps([
                        "Зимой содержите в прохладе (16-18°C)",
                        "Повышайте влажность опрыскиванием",
                        "Не переставляйте без необходимости",
                        "Может сбрасывать нижние ветки при стрессе"
                    ]),
                    "category_ids": [0],  # Лиственные (хотя хвойное, но категории ограничены)
                    "climate_zone_ids": [1, 2],  # Субтропический, Умеренный
                    "tag_ids": [5, 15]  # Для интерьера, Коллекционные
                }
            ]
            
            plants = []
            for i, plant_data in enumerate(plants_data):
                print(f"🌿 Создаем растение {i+1}/{len(plants_data)}: {plant_data['name']}")
                
                # Извлекаем ID связей
                category_ids = plant_data.pop("category_ids", [])
                climate_zone_ids = plant_data.pop("climate_zone_ids", [])
                tag_ids = plant_data.pop("tag_ids", [])
                
                # Создаем растение
                plant = Plant(**plant_data)
                session.add(plant)
                await session.flush()  # Фиксируем растение перед добавлением связей
                
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
            
            await session.flush()
            print(f"✅ Создано {len(plants)} растений")
            
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
                
                # Нефролепис
                {"plant_id": plants[5].id, "url": "/images/plants/nephrolepis-1.jpg", 
                 "alt": "Нефролепис", "title": "Папоротник Нефролепис", 
                 "is_primary": True},
                
                # Хамедорея
                {"plant_id": plants[6].id, "url": "/images/plants/chamaedorea-1.jpg", 
                 "alt": "Хамедорея изящная", "title": "Горная пальма", 
                 "is_primary": True},
                
                # Базилик
                {"plant_id": plants[7].id, "url": "/images/plants/basil-1.jpg", 
                 "alt": "Базилик", "title": "Свежие листья базилика", 
                 "is_primary": True},
                
                # Томат Черри
                {"plant_id": plants[8].id, "url": "/images/plants/cherry-tomato-1.jpg", 
                 "alt": "Томат Черри", "title": "Куст томата с плодами", 
                 "is_primary": True},
                
                # Лимон Мейера
                {"plant_id": plants[9].id, "url": "/images/plants/meyer-lemon-1.jpg", 
                 "alt": "Лимон Мейера", "title": "Лимонное дерево с плодами", 
                 "is_primary": True},
                
                # Эхинокактус
                {"plant_id": plants[10].id, "url": "/images/plants/golden-barrel-1.jpg", 
                 "alt": "Эхинокактус Грузони", "title": "Золотая бочка", 
                 "is_primary": True},
                
                # Анубиас
                {"plant_id": plants[11].id, "url": "/images/plants/anubias-nana-1.jpg", 
                 "alt": "Анубиас Нана", "title": "Аквариумное растение", 
                 "is_primary": True},
                
                # Алоэ Вера
                {"plant_id": plants[12].id, "url": "/images/plants/aloe-vera-1.jpg", 
                 "alt": "Алоэ Вера", "title": "Лечебное алоэ", 
                 "is_primary": True},
                {"plant_id": plants[12].id, "url": "/images/plants/aloe-vera-2.jpg", 
                 "alt": "Цветущее алоэ", "title": "Алоэ с цветоносом"},
                
                # Хлорофитум
                {"plant_id": plants[13].id, "url": "/images/plants/chlorophytum-1.jpg", 
                 "alt": "Хлорофитум хохлатый", "title": "Растение с детками", 
                 "is_primary": True},
                
                # Спатифиллум
                {"plant_id": plants[14].id, "url": "/images/plants/spathiphyllum-1.jpg", 
                 "alt": "Спатифиллум", "title": "Женское счастье", 
                 "is_primary": True},
                
                # Норфолкская сосна
                {"plant_id": plants[15].id, "url": "/images/plants/norfolk-pine-1.jpg", 
                 "alt": "Норфолкская сосна", "title": "Комнатная елка", 
                 "is_primary": True},
            ]
            
            for img_data in images_data:
                image = PlantImage(**img_data)
                session.add(image)
            
            print(f"✅ Создано {len(images_data)} изображений")
            
            # Сохраняем все изменения
            await session.commit()
            print("\n🎉 Все данные успешно добавлены в базу!")
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


async def clear_all_data():
    """Удаляет все данные из таблиц растений (для тестирования)"""
    async for session in get_db():
        try:
            print("🗑️  Удаляем существующие данные...")
            
            # Удаляем в порядке зависимостей
            await session.execute(text("DELETE FROM plant_images"))
            await session.execute(text("DELETE FROM plant_tag"))
            await session.execute(text("DELETE FROM plant_category"))
            await session.execute(text("DELETE FROM plant_climate_zone"))
            await session.execute(text("DELETE FROM plants"))
            await session.execute(text("DELETE FROM tags"))
            await session.execute(text("DELETE FROM plant_categories"))
            await session.execute(text("DELETE FROM climate_zones"))
            
            await session.commit()
            print("✅ Все данные удалены")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при удалении данных: {e}")
            raise
        finally:
            await session.close()
            break



if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Заполнение базы данных растениями")
    parser.add_argument(
        "--clear", 
        action="store_true", 
        help="Очистить все данные перед заполнением"
    )
    parser.add_argument(
        "--clear-only", 
        action="store_true", 
        help="Только очистить данные (не заполнять)"
    )
    
    args = parser.parse_args()
    
    async def main():
        if args.clear or args.clear_only:
            await clear_all_data()
        
        if not args.clear_only:
            await seed_plants_data()
    
    asyncio.run(main())