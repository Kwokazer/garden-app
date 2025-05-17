from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.plant import Plant
from app.domain.models.climate_zone import ClimateZone, plant_to_climate_zone, PlantToClimateZone
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError

class ClimateZoneRepository(BaseRepository[ClimateZone]):
    """Репозиторий для работы с климатическими зонами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, ClimateZone)
    
    async def get_climate_zones(self, skip: int = 0, limit: int = 100) -> List[ClimateZone]:
        """
        Получить список климатических зон с пагинацией
        """
        query = select(ClimateZone).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_climate_zone(self, zone_id: int) -> ClimateZone:
        """
        Получить климатическую зону по ID
        """
        query = select(ClimateZone).filter(ClimateZone.id == zone_id)
        result = await self.session.execute(query)
        zone = result.scalars().first()
        
        if not zone:
            raise EntityNotFoundError("ClimateZone", zone_id)
        
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
        Получить растения для указанной климатической зоны
        """
        # Строим запрос
        query = (
            select(Plant)
            .options(selectinload(Plant.classifications), selectinload(Plant.climate_zones))
            .join(PlantToClimateZone, Plant.id == PlantToClimateZone.plant_id)
            .filter(PlantToClimateZone.climate_zone_id == zone_id)
            .offset(skip).limit(limit)
        )
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_plants_by_climate_zone(self, zone_id: int) -> int:
        """
        Получить количество растений для указанной климатической зоны
        """
        # Строим запрос
        query = (
            select(func.count())
            .select_from(Plant)
            .join(PlantToClimateZone, Plant.id == PlantToClimateZone.plant_id)
            .filter(PlantToClimateZone.climate_zone_id == zone_id)
        )
        
        # Выполняем запрос
        result = await self.session.execute(query)
        return result.scalar()