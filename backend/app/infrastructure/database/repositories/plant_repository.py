from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.plant import Plant, PlantImage
from app.domain.models.plant_category import PlantCategory, plant_to_category
from app.domain.models.climate_zone import ClimateZone, plant_to_climate_zone, PlantToClimateZone
from app.infrastructure.database.repositories.base import BaseRepository

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
        plant_type: Optional[str] = None,
        min_popularity: Optional[int] = None,
        min_hardiness_zone: Optional[int] = None,
        max_hardiness_zone: Optional[int] = None
    ) -> List[Plant]:
        """
        Получить список растений с применением фильтров
        """
        # Начинаем строить запрос
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images)
            )
        )
        
        # Применяем фильтры, если они указаны
        if name_filter:
            query = query.filter(Plant.name.ilike(f"%{name_filter}%"))
        
        if category_id is not None:
        # Фильтрация по классификации через связующую таблицу
            query = query.join(
                plant_to_category,
                Plant.id == plant_to_category.c.plant_id
            ).filter(plant_to_category.c.category_id == category_id)
        
        if climate_zone_id is not None:
            # Фильтрация по климатической зоне через связующую таблицу
            query = query.join(
                plant_to_climate_zone,
                Plant.id == plant_to_climate_zone.c.plant_id
            ).filter(plant_to_climate_zone.c.climate_zone_id == climate_zone_id)
        
        if plant_type:
            query = query.filter(Plant.plant_type == plant_type)
        
        if min_popularity is not None:
            query = query.filter(Plant.popularity_score >= min_popularity)
        
        if min_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_min >= min_hardiness_zone)
        
        if max_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_max <= max_hardiness_zone)
        
        # Применяем пагинацию
        query = query.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_plants(
        self,
        name_filter: Optional[str] = None,
        category_id: Optional[int] = None,
        climate_zone_id: Optional[int] = None,
        plant_type: Optional[str] = None,
        min_popularity: Optional[int] = None,
        min_hardiness_zone: Optional[int] = None,
        max_hardiness_zone: Optional[int] = None
    ) -> int:
        """
        Получить общее количество растений, соответствующих фильтрам
        """
        # Начинаем строить запрос
        query = select(func.count()).select_from(Plant)
        
        # Применяем фильтры, если они указаны
        if name_filter:
            query = query.filter(Plant.name.ilike(f"%{name_filter}%"))
        
        if category_id is not None:
            # Фильтрация по классификации через связующую таблицу
            query = query.join(
                plant_to_category,
                Plant.id == plant_to_category.c.plant_id
            ).filter(plant_to_category.c.category_id == category_id)
        
        if climate_zone_id is not None:
            # Фильтрация по климатической зоне через связующую таблицу
            query = query.join(
                plant_to_climate_zone,
                Plant.id == plant_to_climate_zone.c.plant_id
            ).filter(plant_to_climate_zone.c.climate_zone_id == climate_zone_id)
        
        if plant_type:
            query = query.filter(Plant.plant_type == plant_type)
        
        if min_popularity is not None:
            query = query.filter(Plant.popularity_score >= min_popularity)
        
        if min_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_min >= min_hardiness_zone)
        
        if max_hardiness_zone is not None:
            query = query.filter(Plant.hardiness_zone_max <= max_hardiness_zone)
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return result.scalar()
    
    # Добавьте в PlantRepository

    async def get_plant_with_details(self, plant_id: int) -> Plant:
        """
        Получить детальную информацию о растении по ID со всеми связанными данными
        """
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images)
            )
            .filter(Plant.id == plant_id)
        )
        result = await self.session.execute(query)
        plant = result.scalars().first()
        
        if not plant:
            raise Exception(f"Растение с ID {plant_id} не найдено")
        
        return plant
    
        
    
    async def add_category_to_plant(self, plant_id: int, category_id: int) -> None:
        """
        Добавить классификацию к растению
        """
        # Проверяем, что классификация существует
        query = select(PlantCategory).filter(PlantCategory.id == category_id)
        result = await self.session.execute(query)
        category = result.scalars().first()
        
        if not category:
            raise Exception(f"Классификация с ID {category_id} не найдена")
        
        # Проверяем, что растение существует
        plant = await self.get_plant(plant_id)
        
        # Проверяем, существует ли уже связь
        query = select(PlantToCategory).filter(
            PlantToCategory.plant_id == plant_id,
            PlantToCategory.category_id == category_id
        )
        result = await self.session.execute(query)
        existing_relation = result.scalars().first()
        
        # Если связи нет, добавляем ее
        if not existing_relation:
            new_relation = PlantToCategory(
                plant_id=plant_id,
                category_id=category_id
            )
            self.session.add(new_relation)
            await self.session.commit()
    
    async def remove_category_from_plant(self, plant_id: int, category_id: int) -> None:
        """
        Удалить классификацию у растения
        """
        # Находим существующую связь
        query = select(PlantToCategory).filter(
            PlantToCategory.plant_id == plant_id,
            PlantToCategory.category_id == category_id
        )
        result = await self.session.execute(query)
        relation = result.scalars().first()
        
        # Если связь существует, удаляем ее
        if relation:
            await self.session.delete(relation)
            await self.session.commit()
    
    async def add_climate_zone_to_plant(self, plant_id: int, zone_id: int) -> None:
        """
        Добавить климатическую зону к растению
        """
        # Проверяем, что зона существует
        query = select(ClimateZone).filter(ClimateZone.id == zone_id)
        result = await self.session.execute(query)
        zone = result.scalars().first()
        
        if not zone:
            raise Exception(f"Климатическая зона с ID {zone_id} не найдена")
        
        # Проверяем, что растение существует
        plant = await self.get_plant(plant_id)
        
        # Проверяем, существует ли уже связь
        query = select(PlantToClimateZone).filter(
            PlantToClimateZone.plant_id == plant_id,
            PlantToClimateZone.climate_zone_id == zone_id
        )
        result = await self.session.execute(query)
        existing_relation = result.scalars().first()
        
        # Если связи нет, добавляем ее
        if not existing_relation:
            new_relation = PlantToClimateZone(
                plant_id=plant_id,
                climate_zone_id=zone_id
            )
            self.session.add(new_relation)
            await self.session.commit()
    
    async def remove_climate_zone_from_plant(self, plant_id: int, zone_id: int) -> None:
        """
        Удалить климатическую зону у растения
        """
        # Находим существующую связь
        query = select(PlantToClimateZone).filter(
            PlantToClimateZone.plant_id == plant_id,
            PlantToClimateZone.climate_zone_id == zone_id
        )
        result = await self.session.execute(query)
        relation = result.scalars().first()
        
        # Если связь существует, удаляем ее
        if relation:
            await self.session.delete(relation)
            await self.session.commit()
    
    async def add_image_to_plant(self, plant_id: int, image_data: Dict[str, Any]) -> PlantImage:
        """
        Добавить изображение к растению
        """
        # Проверяем, что растение существует
        await self.get_plant(plant_id)
        
        # Если это первичное изображение, сбрасываем флаг is_primary у других изображений
        if image_data.get("is_primary", False):
            query = (
                select(PlantImage)
                .filter(
                    PlantImage.plant_id == plant_id,
                    PlantImage.is_primary == True
                )
            )
            result = await self.session.execute(query)
            primary_images = result.scalars().all()
            
            for image in primary_images:
                image.is_primary = False
        
        # Создаем новое изображение
        image = PlantImage(plant_id=plant_id, **image_data)
        self.session.add(image)
        await self.session.commit()
        
        return image
    

    async def get_plants_with_filters(
    self,
    skip: int = 0,
    limit: int = 20,
    filters: Optional[Plant] = None) -> tuple[List[Plant], int]:
        """
        Получить список растений с применением фильтров из объекта PlantFilterParams
        """
        # Значения фильтров по умолчанию
        name_filter = None
        category_id = None
        climate_zone_id = None
        plant_type = None
        min_popularity = None
        min_hardiness_zone = None
        max_hardiness_zone = None
    
        # Применяем фильтры, если они указаны
        if filters:
            name_filter = filters.name
            category_id = filters.category_id
            climate_zone_id = filters.climate_zone_id
            plant_type = filters.plant_type.value if filters.plant_type else None
            min_popularity = filters.min_popularity
            min_hardiness_zone = filters.min_hardiness_zone
            max_hardiness_zone = filters.max_hardiness_zone
        
        # Получаем растения с применением фильтров
        plants = await self.get_plants(
            skip=skip,
            limit=limit,
            name_filter=name_filter,
            category_id=category_id,
            climate_zone_id=climate_zone_id,
            plant_type=plant_type,
            min_popularity=min_popularity,
            min_hardiness_zone=min_hardiness_zone,
            max_hardiness_zone=max_hardiness_zone
        )
    
        # Получаем общее количество растений с этими фильтрами
        total = await self.count_plants(
            name_filter=name_filter,
            category_id=category_id,
            climate_zone_id=climate_zone_id,
            plant_type=plant_type,
            min_popularity=min_popularity,
            min_hardiness_zone=min_hardiness_zone,
            max_hardiness_zone=max_hardiness_zone
        )
        
        return plants, total

    async def remove_image_from_plant(self, image_id: int) -> bool:
        """
        Удалить изображение у растения
        """
        # Проверяем, что изображение существует
        query = select(PlantImage).filter(PlantImage.id == image_id)
        result = await self.session.execute(query)
        image = result.scalars().first()
        
        if not image:
            raise Exception(f"Изображение с ID {image_id} не найдено")
        
        # Удаляем изображение
        await self.session.delete(image)
        await self.session.commit()
        
        return True
    

class ClimateZoneRepository(BaseRepository[ClimateZone]):
    """Репозиторий для работы с климатическими зонами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ClimateZone)
    
    async def get_climate_zones(self, skip: int = 0, limit: int = 100) -> List[ClimateZone]:
        """
        Получить список климатических зон
        """
        query = select(ClimateZone).offset(skip).limit(limit)
        result = await self.session.execute(query)
        
        return result.scalars().all()
    
    async def get_climate_zone(self, zone_id: int) -> ClimateZone:
        """
        Получить климатическую зону по ID
        """
        query = select(ClimateZone).filter(ClimateZone.id == zone_id)
        result = await self.session.execute(query)
        zone = result.scalars().first()
        
        if not zone:
            raise Exception(f"Климатическая зона с ID {zone_id} не найдена")
        
        return zone
    
    async def get_climate_zone_by_number(self, zone_number: int) -> Optional[ClimateZone]:
        """
        Получить климатическую зону по номеру
        """
        query = select(ClimateZone).filter(ClimateZone.zone_number == zone_number)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_plants_by_climate_zone(self, zone_id: int, skip: int = 0, limit: int = 20) -> List[Plant]:
        """
        Получить растения по климатической зоне
        """
        query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images)
            )
            .join(plant_to_climate_zone, Plant.id == plant_to_climate_zone.c.plant_id)
            .filter(plant_to_climate_zone.c.climate_zone_id == zone_id)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def count_plants_by_climate_zone(self, zone_id: int) -> int:
        """
        Получить общее количество растений в климатической зоне
        """
        query = (
            select(func.count())
            .select_from(Plant)
            .join(plant_to_climate_zone, Plant.id == plant_to_climate_zone.c.plant_id)
            .filter(plant_to_climate_zone.c.climate_zone_id == zone_id)
        )
        
        result = await self.session.execute(query)
        return result.scalar()
    

    