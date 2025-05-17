from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import (BaseService, NotFoundError,
                                           ValidationError)
from app.domain.models.climate_zone import ClimateZone
from app.domain.schemas.climate_zone import (ClimateZoneCreate, ClimateZoneResponse,
                                            ClimateZoneUpdate)
from app.domain.schemas.plant import PlantListResponse, PlantResponse
from app.infrastructure.database.repositories import (
    ClimateZoneRepository, PlantRepository)
from app.infrastructure.cache.plant_cache import PlantCache


class ClimateZoneService(BaseService):
    """
    Сервис для работы с климатическими зонами
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCache] = None):
        super().__init__()
        self.session = session
        self.climate_zone_repository = ClimateZoneRepository(session)
        self.plant_cache = plant_cache
    
    async def get_climate_zones(self, skip: int = 0, limit: int = 100) -> List[ClimateZoneResponse]:
        """
        Получить список климатических зон
        """
        # Пытаемся получить данные из кэша, если кэш доступен
        cache_key = f"climate_zones:list:{skip}:{limit}"
        cached_data = None
        
        if self.plant_cache:
            cached_data = await self.plant_cache.redis.get(cache_key)
            if cached_data:
                self._log_info(f"Получены климатические зоны из кэша: {cache_key}")
                return [ClimateZoneResponse.model_validate(zone) for zone in cached_data]
        
        # Если данных нет в кэше, получаем из базы
        climate_zones = await self.climate_zone_repository.get_climate_zones(skip, limit)
        result = [ClimateZoneResponse.model_validate(zone) for zone in climate_zones]
        
        # Сохраняем в кэш, если он доступен
        if self.plant_cache:
            data_to_cache = [zone.model_dump() for zone in result]
            await self.plant_cache.redis.set(cache_key, data_to_cache, expires=3600)  # Кэш на 1 час
            self._log_info(f"Сохранены климатические зоны в кэш: {cache_key}")
            
        return result
    
    async def get_climate_zone(self, zone_id: int) -> ClimateZoneResponse:
        """
        Получить климатическую зону по ID
        """
        try:
            zone = await self.climate_zone_repository.get_climate_zone(zone_id)
            if not zone:
                raise NotFoundError("ClimateZone", zone_id)
            return ClimateZoneResponse.model_validate(zone)
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении климатической зоны с ID {zone_id}", e)
            raise ValidationError(f"Не удалось получить климатическую зону: {str(e)}")
    
    async def create_climate_zone(self, zone_data: ClimateZoneCreate) -> ClimateZoneResponse:
        """
        Создать новую климатическую зону
        """
        try:
            # Проверяем, что зона с таким же номером еще не существует
            existing_zone = await self.climate_zone_repository.get_climate_zone_by_number(zone_data.zone_number)
            if existing_zone:
                raise ValidationError(f"Климатическая зона с номером {zone_data.zone_number} уже существует")
            
            # Создаем климатическую зону
            create_data = zone_data.model_dump()
            zone = await self.climate_zone_repository.create(create_data)
            
            # Инвалидируем кэш зон
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша зон
                pass
            
            return ClimateZoneResponse.model_validate(zone)
        except ValidationError:
            raise
        except Exception as e:
            self._log_error("Ошибка при создании климатической зоны", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось создать климатическую зону: {str(e)}")
    
    async def update_climate_zone(self, zone_id: int, zone_data: ClimateZoneUpdate) -> ClimateZoneResponse:
        """
        Обновить климатическую зону
        """
        try:
            # Проверяем, что зона существует
            existing_zone = await self.climate_zone_repository.get_climate_zone(zone_id)
            if not existing_zone:
                raise NotFoundError("ClimateZone", zone_id)
            
            # Если меняется номер зоны, проверяем, что он не конфликтует с другими зонами
            if zone_data.zone_number is not None and zone_data.zone_number != existing_zone.zone_number:
                zone_number_check = await self.climate_zone_repository.get_climate_zone_by_number(zone_data.zone_number)
                if zone_number_check and zone_number_check.id != zone_id:
                    raise ValidationError(f"Климатическая зона с номером {zone_data.zone_number} уже существует")
            
            # Обновляем зону
            update_data = zone_data.model_dump(exclude_unset=True)
            zone = await self.climate_zone_repository.update(zone_id, update_data)
            
            # Инвалидируем кэш зон
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша зон
                pass
            
            return ClimateZoneResponse.model_validate(zone)
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении климатической зоны с ID {zone_id}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось обновить климатическую зону: {str(e)}")
    
    async def delete_climate_zone(self, zone_id: int) -> bool:
        """
        Удалить климатическую зону
        """
        try:
            # Проверяем, что зона существует
            existing_zone = await self.climate_zone_repository.get_climate_zone(zone_id)
            if not existing_zone:
                raise NotFoundError("ClimateZone", zone_id)
            
            # Проверяем, что нет растений в этой зоне
            plant_count = await self.climate_zone_repository.count_plants_by_climate_zone(zone_id)
            if plant_count > 0:
                raise ValidationError(f"Невозможно удалить климатическую зону, так как она содержит {plant_count} растений")
            
            # Удаляем зону
            result = await self.climate_zone_repository.delete(zone_id)
            
            # Инвалидируем кэш зон
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша зон
                pass
            
            return result
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении климатической зоны с ID {zone_id}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось удалить климатическую зону: {str(e)}")
    
    async def get_plants_by_climate_zone(self, zone_id: int, skip: int = 0, limit: int = 20) -> PlantListResponse:
        """
        Получить растения по климатической зоне
        """
        try:
            # Проверяем, что зона существует
            existing_zone = await self.climate_zone_repository.get_climate_zone(zone_id)
            if not existing_zone:
                raise NotFoundError("ClimateZone", zone_id)
            
            # Пытаемся получить данные из кэша, если кэш доступен
            if self.plant_cache:
                cached_result = await self.plant_cache.get_climate_zone_plants(zone_id, skip, limit)
                if cached_result:
                    self._log_info(f"Получены растения для климатической зоны {zone_id} из кэша")
                    return cached_result
            
            # Если данных нет в кэше, получаем из базы
            plants = await self.climate_zone_repository.get_plants_by_climate_zone(zone_id, skip, limit)
            total = await self.climate_zone_repository.count_plants_by_climate_zone(zone_id)
            
            # Преобразуем результаты в схему ответа
            items = [PlantResponse.model_validate(plant) for plant in plants]
            
            # Расчет количества страниц
            pages = (total + limit - 1) // limit if limit > 0 else 0
            
            # Формируем ответ с пагинацией
            result = PlantListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit,
                pages=pages
            )
            
            # Сохраняем результат в кэш, если кэш доступен
            if self.plant_cache:
                await self.plant_cache.set_climate_zone_plants(zone_id, result, skip, limit)
                self._log_info(f"Сохранены растения для климатической зоны {zone_id} в кэш")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении растений для климатической зоны {zone_id}", e)
            raise ValidationError(f"Не удалось получить растения по климатической зоне: {str(e)}") 