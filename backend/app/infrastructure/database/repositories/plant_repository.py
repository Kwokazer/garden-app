import json
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.plant import Plant
from app.domain.models.plant_image import PlantImage
from app.domain.models.plant_category import PlantCategory, plant_to_category, PlantToCategory
from app.domain.models.climate_zone import ClimateZone, plant_to_climate_zone, PlantToClimateZone
from app.domain.models.tag import Tag, plant_tag
from app.domain.schemas.plant import PlantFilterParams
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError


class PlantRepository(BaseRepository[Plant]):
    """Репозиторий для работы с растениями"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Plant)
    
    async def get_plants(
        self,
        skip: int = 0,
        limit: int = 20,
        name_filter: Optional[str] = None,
        category_id: Optional[int] = None,
        climate_zone_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        plant_type: Optional[str] = None,
        life_cycle: Optional[str] = None,
        min_popularity: Optional[int] = None,
        min_hardiness_zone: Optional[int] = None,
        max_hardiness_zone: Optional[int] = None,
        watering_frequency: Optional[str] = None,
        light_level: Optional[str] = None,
        care_difficulty: Optional[str] = None,
        is_toxic: Optional[bool] = None,
        min_height: Optional[float] = None,
        max_height: Optional[float] = None,
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None
    ) -> List[Plant]:
        """
        Получить список растений с применением фильтров
        """
        # Начинаем строить запрос с загрузкой связанных данных
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images),
                selectinload(Plant.tags)
            )
        )
        
        # Применяем фильтры, если они указаны
        if name_filter:
            query = query.filter(or_(
                Plant.name.ilike(f"%{name_filter}%"),
                Plant.latin_name.ilike(f"%{name_filter}%")
            ))
        
        if category_id is not None:
            # Фильтрация по категории через связующую таблицу
            query = query.join(
                plant_to_category,
                Plant.id == plant_to_category.c.plant_id
            ).filter(plant_to_category.c.category_id == category_id)
        
        if climate_zone_id is not None:
            query = query.join(
                PlantToClimateZone,
                Plant.id == PlantToClimateZone.plant_id
            ).filter(PlantToClimateZone.climate_zone_id == climate_zone_id)
        
        if tag_id is not None:
            # Фильтрация по тегу через связующую таблицу
            query = query.join(
                plant_tag,
                Plant.id == plant_tag.c.plant_id
            ).filter(plant_tag.c.tag_id == tag_id)
        
        if plant_type:
            query = query.filter(Plant.plant_type == plant_type)
        
        if life_cycle:
            query = query.filter(Plant.life_cycle == life_cycle)
        
        if min_popularity is not None:
            query = query.filter(Plant.popularity_score >= min_popularity)
        
        if min_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_min >= min_hardiness_zone)
        
        if max_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_max <= max_hardiness_zone)
        
        if watering_frequency:
            query = query.filter(Plant.watering_frequency == watering_frequency)
        
        if light_level:
            query = query.filter(Plant.light_level == light_level)
        
        if care_difficulty:
            query = query.filter(Plant.care_difficulty == care_difficulty)
        
        if is_toxic is not None:
            query = query.filter(Plant.is_toxic == is_toxic)
        
        if min_height is not None:
            query = query.filter(Plant.height_min >= min_height)
        
        if max_height is not None:
            query = query.filter(Plant.height_max <= max_height)
        
        if min_temperature is not None:
            query = query.filter(Plant.temperature_min >= min_temperature)
        
        if max_temperature is not None:
            query = query.filter(Plant.temperature_max <= max_temperature)
        
        # Сортировка по популярности, затем по имени
        query = query.order_by(Plant.popularity_score.desc(), Plant.name)
        
        # Применяем пагинацию
        query = query.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_plants(
        self,
        name_filter: Optional[str] = None,
        category_id: Optional[int] = None,
        climate_zone_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        plant_type: Optional[str] = None,
        life_cycle: Optional[str] = None,
        min_popularity: Optional[int] = None,
        min_hardiness_zone: Optional[int] = None,
        max_hardiness_zone: Optional[int] = None,
        watering_frequency: Optional[str] = None,
        light_level: Optional[str] = None,
        care_difficulty: Optional[str] = None,
        is_toxic: Optional[bool] = None,
        min_height: Optional[float] = None,
        max_height: Optional[float] = None,
        min_temperature: Optional[float] = None,
        max_temperature: Optional[float] = None
    ) -> int:
        """
        Получить общее количество растений, соответствующих фильтрам
        """
        # Начинаем строить запрос
        query = select(func.count()).select_from(Plant)
        
        # Применяем те же фильтры, что и в get_plants
        if name_filter:
            query = query.filter(or_(
                Plant.name.ilike(f"%{name_filter}%"),
                Plant.latin_name.ilike(f"%{name_filter}%")
            ))
        
        if category_id is not None:
            query = query.join(
                plant_to_category,
                Plant.id == plant_to_category.c.plant_id
            ).filter(plant_to_category.c.category_id == category_id)
        
        if climate_zone_id is not None:
            query = query.join(
                PlantToClimateZone,
                Plant.id == PlantToClimateZone.plant_id
            ).filter(PlantToClimateZone.climate_zone_id == climate_zone_id)
        
        if tag_id is not None:
            query = query.join(
                plant_tag,
                Plant.id == plant_tag.c.plant_id
            ).filter(plant_tag.c.tag_id == tag_id)
        
        if plant_type:
            query = query.filter(Plant.plant_type == plant_type)
        
        if life_cycle:
            query = query.filter(Plant.life_cycle == life_cycle)
        
        if min_popularity is not None:
            query = query.filter(Plant.popularity_score >= min_popularity)
        
        if min_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_min >= min_hardiness_zone)
        
        if max_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_max <= max_hardiness_zone)
        
        if watering_frequency:
            query = query.filter(Plant.watering_frequency == watering_frequency)
        
        if light_level:
            query = query.filter(Plant.light_level == light_level)
        
        if care_difficulty:
            query = query.filter(Plant.care_difficulty == care_difficulty)
        
        if is_toxic is not None:
            query = query.filter(Plant.is_toxic == is_toxic)
        
        if min_height is not None:
            query = query.filter(Plant.height_min >= min_height)
        
        if max_height is not None:
            query = query.filter(Plant.height_max <= max_height)
        
        if min_temperature is not None:
            query = query.filter(Plant.temperature_min >= min_temperature)
        
        if max_temperature is not None:
            query = query.filter(Plant.temperature_max <= max_temperature)
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def get_plants_with_filters(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[PlantFilterParams] = None
    ) -> tuple[List[Plant], int]:
        """
        Получить список растений с применением фильтров из объекта PlantFilterParams
        """
        # Значения фильтров по умолчанию
        filter_kwargs = {}
        
        # Применяем фильтры, если они указаны
        if filters:
            if filters.name:
                filter_kwargs["name_filter"] = filters.name
            if filters.category_id:
                filter_kwargs["category_id"] = filters.category_id
            if filters.climate_zone_id:
                filter_kwargs["climate_zone_id"] = filters.climate_zone_id
            if filters.tag_id:
                filter_kwargs["tag_id"] = filters.tag_id
            if filters.plant_type:
                filter_kwargs["plant_type"] = filters.plant_type.value
            if filters.life_cycle:
                filter_kwargs["life_cycle"] = filters.life_cycle.value
            if filters.min_popularity is not None:
                filter_kwargs["min_popularity"] = filters.min_popularity
            if filters.min_hardiness_zone:
                filter_kwargs["min_hardiness_zone"] = filters.min_hardiness_zone
            if filters.max_hardiness_zone:
                filter_kwargs["max_hardiness_zone"] = filters.max_hardiness_zone
            if filters.watering_frequency:
                filter_kwargs["watering_frequency"] = filters.watering_frequency.value
            if filters.light_level:
                filter_kwargs["light_level"] = filters.light_level.value
            if filters.care_difficulty:
                filter_kwargs["care_difficulty"] = filters.care_difficulty.value
            if filters.is_toxic is not None:
                filter_kwargs["is_toxic"] = filters.is_toxic
            if filters.min_height:
                filter_kwargs["min_height"] = filters.min_height
            if filters.max_height:
                filter_kwargs["max_height"] = filters.max_height
            if filters.min_temperature:
                filter_kwargs["min_temperature"] = filters.min_temperature
            if filters.max_temperature:
                filter_kwargs["max_temperature"] = filters.max_temperature
        
        # Получаем растения с применением фильтров
        plants = await self.get_plants(skip=skip, limit=limit, **filter_kwargs)
        
        # Получаем общее количество растений с этими фильтрами
        total = await self.count_plants(**filter_kwargs)
        
        return plants, total
    
    async def get_plant_with_details(self, plant_id: int) -> Plant:
        """
        Получить детальную информацию о растении по ID со всеми связанными данными
        """
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images),
                selectinload(Plant.tags)
            )
            .filter(Plant.id == plant_id)
        )
        result = await self.session.execute(query)
        plant = result.scalars().first()
        
        if not plant:
            raise EntityNotFoundError("Plant", plant_id)
        
        return plant
    
    async def create_plant(
        self, 
        plant_data: Dict[str, Any], 
        category_ids: List[int] = None,
        climate_zone_ids: List[int] = None,
        tag_ids: List[int] = None
    ) -> Plant:
        """
        Создать новое растение со связанными данными
        """
        # Создаем растение
        plant = Plant(**plant_data)
        self.session.add(plant)
        await self.session.flush()  # Получаем ID растения
        
        # Добавляем категории
        if category_ids:
            for category_id in category_ids:
                association = PlantToCategory(plant_id=plant.id, category_id=category_id)
                self.session.add(association)
        
        # Добавляем климатические зоны
        if climate_zone_ids:
            for zone_id in climate_zone_ids:
                association = PlantToClimateZone(plant_id=plant.id, climate_zone_id=zone_id)
                self.session.add(association)
        
        # Добавляем теги
        if tag_ids:
            for tag_id in tag_ids:
                # Используем raw SQL для добавления связи через таблицу plant_tag
                stmt = plant_tag.insert().values(plant_id=plant.id, tag_id=tag_id)
                await self.session.execute(stmt)
        
        await self.session.commit()
        return plant
    
    async def update_plant(
        self,
        plant_id: int,
        plant_data: Dict[str, Any],
        category_ids: List[int] = None,
        climate_zone_ids: List[int] = None,
        tag_ids: List[int] = None
    ) -> Plant:
        """
        Обновить растение со связанными данными
        """
        # Получаем растение
        plant = await self.get_by_id(plant_id)
        if not plant:
            raise EntityNotFoundError("Plant", plant_id)
        
        # Обновляем базовые поля
        for key, value in plant_data.items():
            if hasattr(plant, key):
                setattr(plant, key, value)
        
        # Обновляем категории, если переданы
        if category_ids is not None:
            # Удаляем старые связи
            await self.session.execute(
                plant_to_category.delete().where(plant_to_category.c.plant_id == plant_id)
            )
            # Добавляем новые связи
            for category_id in category_ids:
                association = PlantToCategory(plant_id=plant_id, category_id=category_id)
                self.session.add(association)
        
        # Обновляем климатические зоны, если переданы
        if climate_zone_ids is not None:
            # Удаляем старые связи
            await self.session.execute(
                plant_to_climate_zone.delete().where(plant_to_climate_zone.c.plant_id == plant_id)
            )
            # Добавляем новые связи
            for zone_id in climate_zone_ids:
                association = PlantToClimateZone(plant_id=plant_id, climate_zone_id=zone_id)
                self.session.add(association)
        
        # Обновляем теги, если переданы
        if tag_ids is not None:
            # Удаляем старые связи
            await self.session.execute(
                plant_tag.delete().where(plant_tag.c.plant_id == plant_id)
            )
            # Добавляем новые связи
            for tag_id in tag_ids:
                stmt = plant_tag.insert().values(plant_id=plant_id, tag_id=tag_id)
                await self.session.execute(stmt)
        
        await self.session.commit()
        return plant
    
    async def delete_plant(self, plant_id: int) -> bool:
        """
        Удалить растение со всеми связанными данными
        """
        plant = await self.get_by_id(plant_id)
        if not plant:
            raise EntityNotFoundError("Plant", plant_id)
        
        # SQLAlchemy автоматически удалит связанные записи благодаря cascade
        await self.session.delete(plant)
        await self.session.commit()
        return True
    
    async def add_image(self, image_data: Dict[str, Any]) -> PlantImage:
        """
        Добавить изображение к растению
        """
        # Если это первичное изображение, сбрасываем флаг is_primary у других изображений
        if image_data.get("is_primary", False):
            query = (
                select(PlantImage)
                .filter(
                    PlantImage.plant_id == image_data["plant_id"],
                    PlantImage.is_primary == True
                )
            )
            result = await self.session.execute(query)
            primary_images = result.scalars().all()
            
            for image in primary_images:
                image.is_primary = False
        
        # Создаем новое изображение
        image = PlantImage(**image_data)
        self.session.add(image)
        await self.session.commit()
        
        return image
    
    async def get_image(self, image_id: int) -> Optional[PlantImage]:
        """
        Получить изображение по ID
        """
        query = select(PlantImage).filter(PlantImage.id == image_id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def remove_image(self, image_id: int) -> bool:
        """
        Удалить изображение растения
        """
        image = await self.get_image(image_id)
        if not image:
            raise EntityNotFoundError("PlantImage", image_id)
        
        await self.session.delete(image)
        await self.session.commit()
        return True
    
    async def search_plants(
        self, 
        search_query: str, 
        skip: int = 0, 
        limit: int = 20,
        filters: Optional[PlantFilterParams] = None
    ) -> tuple[List[Plant], int]:
        """
        Полнотекстовый поиск растений с фильтрацией
        """
        # Создаем поисковый запрос
        search_term = f"%{search_query.lower()}%"
        search_filter = or_(
            func.lower(Plant.name).like(search_term),
            func.lower(Plant.latin_name).like(search_term),
            func.lower(Plant.description).like(search_term)
        )
        
        # Базовый запрос с поиском
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images),
                selectinload(Plant.tags)
            )
            .filter(search_filter)
        )
        
        count_query = select(func.count()).select_from(Plant).filter(search_filter)
        
        # Применяем дополнительные фильтры, если они есть
        if filters:
            additional_filters = []
            
            if filters.category_id:
                query = query.join(plant_to_category, Plant.id == plant_to_category.c.plant_id)
                count_query = count_query.join(plant_to_category, Plant.id == plant_to_category.c.plant_id)
                additional_filters.append(plant_to_category.c.category_id == filters.category_id)
            
            if filters.climate_zone_id:
                query = query.join(plant_to_climate_zone, Plant.id == plant_to_climate_zone.c.plant_id)
                count_query = count_query.join(plant_to_climate_zone, Plant.id == plant_to_climate_zone.c.plant_id)
                additional_filters.append(plant_to_climate_zone.c.climate_zone_id == filters.climate_zone_id)
            
            if filters.tag_id:
                query = query.join(plant_tag, Plant.id == plant_tag.c.plant_id)
                count_query = count_query.join(plant_tag, Plant.id == plant_tag.c.plant_id)
                additional_filters.append(plant_tag.c.tag_id == filters.tag_id)
            
            if filters.plant_type:
                additional_filters.append(Plant.plant_type == filters.plant_type)
            
            if filters.life_cycle:
                additional_filters.append(Plant.life_cycle == filters.life_cycle)
            
            if filters.min_popularity is not None:
                additional_filters.append(Plant.popularity_score >= filters.min_popularity)
            
            if filters.watering_frequency:
                additional_filters.append(Plant.watering_frequency == filters.watering_frequency)
            
            if filters.light_level:
                additional_filters.append(Plant.light_level == filters.light_level)
            
            if filters.care_difficulty:
                additional_filters.append(Plant.care_difficulty == filters.care_difficulty)
            
            if filters.is_toxic is not None:
                additional_filters.append(Plant.is_toxic == filters.is_toxic)
            
            # Применяем все дополнительные фильтры
            if additional_filters:
                combined_filter = and_(*additional_filters)
                query = query.filter(combined_filter)
                count_query = count_query.filter(combined_filter)
        
        # Получаем общее количество
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Применяем сортировку, пагинацию и выполняем запрос
        query = query.order_by(Plant.popularity_score.desc(), Plant.name)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        plants = list(result.scalars().all())
        
        return plants, total