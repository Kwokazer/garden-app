from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.plant import Plant
from app.domain.models.plant_category import PlantCategory, PlantToCategory
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError

class PlantCategoryRepository(BaseRepository[PlantCategory]):
    """Репозиторий для работы с категориями растений"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, PlantCategory)
    
    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[PlantCategory]:
        """
        Получить список категорий с пагинацией
        """
        query = select(PlantCategory).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_category(self, category_id: int) -> PlantCategory:
        """
        Получить категорию по ID
        """
        query = select(PlantCategory).filter(PlantCategory.id == category_id)
        result = await self.session.execute(query)
        category = result.scalars().first()
        
        if not category:
            raise EntityNotFoundError("PlantCategory", category_id)
        
        return category
    
    async def get_category_by_name(self, name: str) -> Optional[PlantCategory]:
        """
        Получить категорию по имени
        """
        query = select(PlantCategory).filter(PlantCategory.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_subcategories(self, parent_id: int) -> List[PlantCategory]:
        """
        Получить список подкатегорий для указанной родительской категории
        """
        query = select(PlantCategory).filter(PlantCategory.parent_id == parent_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_plants_by_category(self, category_id: int, skip: int = 0, limit: int = 20) -> List[Plant]:
        """
        Получить растения для указанной категории
        """
        # Строим запрос
        query = (
            select(Plant)
            .options(selectinload(Plant.categories), selectinload(Plant.climate_zones))
            .join(PlantToCategory, Plant.id == PlantToCategory.plant_id)
            .filter(PlantToCategory.category_id == category_id)
            .offset(skip).limit(limit)
        )
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_plants_by_category(self, category_id: int) -> int:
        """
        Получить количество растений для указанной категории
        """
        # Строим запрос
        query = (
            select(func.count())
            .select_from(Plant)
            .join(PlantToCategory, Plant.id == PlantToCategory.plant_id)
            .filter(PlantToCategory.category_id == category_id)
        )
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return result.scalar() 