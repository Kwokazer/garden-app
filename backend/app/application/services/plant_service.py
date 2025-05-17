from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import (BaseService, NotFoundError,
                                           ValidationError)
from app.domain.models.plant import Plant
from app.domain.models.plant_image import PlantImage
from app.domain.models.plant_category import PlantCategory
from app.domain.models.climate_zone import ClimateZone
from app.domain.schemas.plant import (PlantCreate, PlantFilterParams, 
                                      PlantListResponse, PlantResponse, PlantUpdate)
from app.domain.schemas.plant_category import (PlantCategoryCreate, PlantCategoryResponse, 
                                              PlantCategoryUpdate)
from app.domain.schemas.plant_image import PlantImageCreate, PlantImageResponse
from app.domain.schemas.climate_zone import (ClimateZoneCreate, ClimateZoneResponse,
                                            ClimateZoneUpdate)
from app.infrastructure.database.repositories import (
    PlantRepository, PlantCategoryRepository, ClimateZoneRepository)
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
                self._log_info(f"Данные получены из кэша: {cache_key}")
                return [ClimateZoneResponse.model_validate(zone) for zone in cached_data]
        
        # Если данных нет в кэше, получаем из базы
        climate_zones = await self.climate_zone_repository.get_climate_zones(skip, limit)
        result = [ClimateZoneResponse.model_validate(zone) for zone in climate_zones]
        
        # Сохраняем в кэш, если он доступен
        if self.plant_cache:
            data_to_cache = [zone.model_dump() for zone in result]
            await self.plant_cache.redis.set(cache_key, data_to_cache, expires=3600)  # Кэш на 1 час
            self._log_info(f"Данные сохранены в кэш: {cache_key}")
            
        return result
    
    async def get_climate_zone(self, zone_id: int) -> ClimateZoneResponse:
        """
        Получить климатическую зону по ID
        """
        try:
            zone = await self.climate_zone_repository.get_climate_zone(zone_id)
            return ClimateZoneResponse.model_validate(zone)
        except Exception as e:
            self._log_error(f"Ошибка при получении климатической зоны с ID {zone_id}", e)
            raise NotFoundError("ClimateZone", zone_id)
    
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
            await self.climate_zone_repository.get_climate_zone(zone_id)
            
            # Если меняется номер зоны, проверяем, что он не конфликтует с другими зонами
            if zone_data.zone_number is not None:
                existing_zone = await self.climate_zone_repository.get_climate_zone_by_number(zone_data.zone_number)
                if existing_zone and existing_zone.id != zone_id:
                    raise ValidationError(f"Климатическая зона с номером {zone_data.zone_number} уже существует")
            
            # Обновляем зону
            update_data = zone_data.model_dump(exclude_unset=True)
            zone = await self.climate_zone_repository.update(zone_id, update_data)
            
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
            await self.climate_zone_repository.get_climate_zone(zone_id)
            
            # Удаляем зону
            result = await self.climate_zone_repository.delete(zone_id)
            return result
        except NotFoundError:
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
            await self.climate_zone_repository.get_climate_zone(zone_id)
            
            # Получаем растения в зоне
            plants = await self.climate_zone_repository.get_plants_by_climate_zone(zone_id, skip, limit)
            
            # Получаем общее количество растений в зоне
            total = await self.climate_zone_repository.count_plants_by_climate_zone(zone_id)
            
            # Преобразуем результаты в схему ответа
            items = [PlantResponse.model_validate(plant) for plant in plants]
            
            # Расчет количества страниц
            pages = (total + limit - 1) // limit if limit > 0 else 0
            
            # Формируем ответ с пагинацией
            return PlantListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit,
                pages=pages
            )
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении растений для климатической зоны с ID {zone_id}", e)
            raise ValidationError(f"Не удалось получить растения по климатической зоне: {str(e)}")

class PlantService(BaseService):
    """
    Сервис для работы с растениями
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCache] = None):
        super().__init__()
        self.session = session
        self.plant_repository = PlantRepository(session)
        self.category_repository = PlantCategoryRepository(session)
        self.climate_zone_repository = ClimateZoneRepository(session)
        self.plant_cache = plant_cache
    
    async def get_plants(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filters: Optional[PlantFilterParams] = None
    ) -> PlantListResponse:
        """
        Получить список растений с применением фильтров и пагинации
        """
        # Пытаемся получить данные из кэша, если кэш доступен
        if self.plant_cache:
            # Преобразуем фильтры в словарь для формирования ключа кэша
            filters_dict = None
            if filters:
                filters_dict = filters.model_dump(exclude_unset=True)
                
            cached_result = await self.plant_cache.get_plants_list(skip, limit, filters_dict)
            if cached_result:
                self._log_info(f"Получен список растений из кэша с пагинацией skip={skip}, limit={limit}")
                return cached_result
    
        try:
            # Если в кэше нет или кэш не доступен, получаем из базы данных
            plants, total = await self.plant_repository.get_plants_with_filters(
                skip=skip,
                limit=limit,
                filters=filters
            )
            
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
            
            # Кэшируем результат, если кэш доступен
            if self.plant_cache:
                await self.plant_cache.set_plants_list(result, skip, limit, filters_dict)
                self._log_info(f"Сохранен список растений в кэш с пагинацией skip={skip}, limit={limit}")
            
            return result
        except Exception as e:
            self._log_error(f"Ошибка при получении списка растений: {str(e)}", e)
            raise ValidationError(f"Не удалось получить список растений: {str(e)}")
    
    async def get_plant(self, plant_id: int) -> PlantResponse:
        """
        Получить растение по ID
        """
        try:
            # Пытаемся получить данные из кэша, если кэш доступен
            if self.plant_cache:
                cached_plant = await self.plant_cache.get_plant_detail(plant_id)
                if cached_plant:
                    self._log_info(f"Получено растение из кэша с ID {plant_id}")
                    return cached_plant
            
            # Если в кэше нет или кэш не доступен, получаем из базы данных
            plant = await self.plant_repository.get_plant_with_details(plant_id)
            
            if not plant:
                raise NotFoundError("Plant", plant_id)
            
            result = PlantResponse.model_validate(plant)
            
            # Кэшируем результат, если кэш доступен
            if self.plant_cache:
                await self.plant_cache.set_plant_detail(result)
                self._log_info(f"Сохранено растение в кэш с ID {plant_id}")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении растения с ID {plant_id}: {str(e)}", e)
            raise ValidationError(f"Не удалось получить растение: {str(e)}")
    
    async def create_plant(self, plant_data: PlantCreate) -> PlantResponse:
        """
        Создать новое растение
        """
        try:
            # Проверяем, что все указанные категории существуют
            if plant_data.category_ids:
                for category_id in plant_data.category_ids:
                    category = await self.category_repository.get_category(category_id)
                    if not category:
                        raise ValidationError(f"Категория с ID {category_id} не найдена")
            
            # Проверяем, что все указанные климатические зоны существуют
            if plant_data.climate_zone_ids:
                for zone_id in plant_data.climate_zone_ids:
                    zone = await self.climate_zone_repository.get_climate_zone(zone_id)
                    if not zone:
                        raise ValidationError(f"Климатическая зона с ID {zone_id} не найдена")
            
            # Извлекаем связанные данные из запроса
            category_ids = plant_data.category_ids or []
            climate_zone_ids = plant_data.climate_zone_ids or []
            
            # Создаем растение в БД
            create_data = plant_data.model_dump(exclude={"category_ids", "climate_zone_ids"})
            plant = await self.plant_repository.create_plant(create_data, category_ids, climate_zone_ids)
            
            # Инвалидируем кэш списков растений, если кэш доступен
            if self.plant_cache:
                await self.plant_cache.invalidate_plants_lists()
                self._log_info("Инвалидирован кэш списков растений")
            
            # Получаем созданное растение с деталями
            created_plant = await self.plant_repository.get_plant_with_details(plant.id)
            
            return PlantResponse.model_validate(created_plant)
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при создании растения: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось создать растение: {str(e)}")
    
    async def update_plant(self, plant_id: int, plant_data: PlantUpdate) -> PlantResponse:
        """
        Обновить растение
        """
        try:
            # Проверяем, что растение существует
            existing_plant = await self.plant_repository.get_plant(plant_id)
            if not existing_plant:
                raise NotFoundError("Plant", plant_id)
            
            # Проверяем, что все указанные категории существуют
            if plant_data.category_ids is not None:
                for category_id in plant_data.category_ids:
                    category = await self.category_repository.get_category(category_id)
                    if not category:
                        raise ValidationError(f"Категория с ID {category_id} не найдена")
            
            # Проверяем, что все указанные климатические зоны существуют
            if plant_data.climate_zone_ids is not None:
                for zone_id in plant_data.climate_zone_ids:
                    zone = await self.climate_zone_repository.get_climate_zone(zone_id)
                    if not zone:
                        raise ValidationError(f"Климатическая зона с ID {zone_id} не найдена")
            
            # Извлекаем связанные данные из запроса
            category_ids = None
            if plant_data.category_ids is not None:
                category_ids = plant_data.category_ids
                
            climate_zone_ids = None
            if plant_data.climate_zone_ids is not None:
                climate_zone_ids = plant_data.climate_zone_ids
            
            # Обновляем данные растения в БД
            update_data = plant_data.model_dump(exclude={"category_ids", "climate_zone_ids"}, exclude_unset=True)
            plant = await self.plant_repository.update_plant(plant_id, update_data, category_ids, climate_zone_ids)
            
            # Инвалидируем кэши, если кэш доступен
            if self.plant_cache:
                # Инвалидируем кэш детальной информации о растении
                await self.plant_cache.invalidate_plant_detail(plant_id)
                self._log_info(f"Инвалидирован кэш растения с ID {plant_id}")
                
                # Инвалидируем кэши списков растений
                await self.plant_cache.invalidate_plants_lists()
                self._log_info("Инвалидирован кэш списков растений")
                
                # Если изменились категории, инвалидируем кэши растений по категориям
                if category_ids is not None:
                    # Получаем текущие категории растения
                    current_plant = await self.plant_repository.get_plant_with_details(plant_id)
                    current_category_ids = [cat.id for cat in current_plant.categories]
                    
                    # Инвалидируем кэши для всех измененных категорий
                    all_affected_category_ids = set(current_category_ids + category_ids)
                    for cat_id in all_affected_category_ids:
                        await self.plant_cache.invalidate_category_plants(cat_id)
                        self._log_info(f"Инвалидирован кэш растений для категории с ID {cat_id}")
                
                # Если изменились климатические зоны, инвалидируем кэши растений по зонам
                if climate_zone_ids is not None:
                    # Получаем текущие зоны растения
                    current_plant = await self.plant_repository.get_plant_with_details(plant_id)
                    current_zone_ids = [zone.id for zone in current_plant.climate_zones]
                    
                    # Инвалидируем кэши для всех измененных зон
                    all_affected_zone_ids = set(current_zone_ids + climate_zone_ids)
                    for zone_id in all_affected_zone_ids:
                        await self.plant_cache.invalidate_climate_zone_plants(zone_id)
                        self._log_info(f"Инвалидирован кэш растений для климатической зоны с ID {zone_id}")
            
            # Получаем обновленное растение с деталями
            updated_plant = await self.plant_repository.get_plant_with_details(plant_id)
            
            return PlantResponse.model_validate(updated_plant)
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении растения с ID {plant_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось обновить растение: {str(e)}")
    
    async def delete_plant(self, plant_id: int) -> bool:
        """
        Удалить растение
        """
        try:
            # Проверяем, что растение существует
            existing_plant = await self.plant_repository.get_plant(plant_id)
            if not existing_plant:
                raise NotFoundError("Plant", plant_id)
            
            # Удаляем растение
            result = await self.plant_repository.delete_plant(plant_id)
            
            # Инвалидируем кэши, если кэш доступен
            if self.plant_cache:
                # Инвалидируем кэш детальной информации о растении
                await self.plant_cache.invalidate_plant_detail(plant_id)
                self._log_info(f"Инвалидирован кэш растения с ID {plant_id}")
                
                # Инвалидируем кэши списков растений
                await self.plant_cache.invalidate_plants_lists()
                self._log_info("Инвалидирован кэш списков растений")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении растения с ID {plant_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось удалить растение: {str(e)}")
    
    async def add_image_to_plant(self, plant_id: int, image_data: PlantImageCreate) -> PlantImageResponse:
        """
        Добавить изображение к растению
        """
        try:
            # Проверяем, что растение существует
            plant = await self.plant_repository.get_plant(plant_id)
            if not plant:
                raise NotFoundError("Plant", plant_id)
            
            # Добавляем изображение
            create_data = image_data.model_dump()
            create_data["plant_id"] = plant_id
            
            image = await self.plant_repository.add_image(create_data)
            
            # Инвалидируем кэш растения
            if self.plant_cache:
                await self.plant_cache.invalidate_plant_detail(plant_id)
                self._log_info(f"Инвалидирован кэш растения с ID {plant_id}")
            
            return PlantImageResponse.model_validate(image)
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при добавлении изображения к растению с ID {plant_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось добавить изображение: {str(e)}")
    
    async def remove_image_from_plant(self, image_id: int) -> bool:
        """
        Удалить изображение растения
        """
        try:
            # Получаем информацию об изображении, чтобы знать, к какому растению оно относится
            image = await self.plant_repository.get_image(image_id)
            if not image:
                raise NotFoundError("PlantImage", image_id)
            
            plant_id = image.plant_id
            
            # Удаляем изображение
            result = await self.plant_repository.remove_image(image_id)
            
            # Инвалидируем кэш растения
            if self.plant_cache:
                await self.plant_cache.invalidate_plant_detail(plant_id)
                self._log_info(f"Инвалидирован кэш растения с ID {plant_id}")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении изображения с ID {image_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось удалить изображение: {str(e)}")

class PlantCategoryService(BaseService):
    """
    Сервис для работы с категориями растений
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCache] = None):
        super().__init__()
        self.session = session
        self.category_repository = PlantCategoryRepository(session)
        self.plant_cache = plant_cache
    
    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[PlantCategoryResponse]:
        """
        Получить список категорий растений
        """
        categories = await self.category_repository.get_categories(skip, limit)
        return [PlantCategoryResponse.model_validate(category) for category in categories]
    
    async def get_category(self, category_id: int) -> PlantCategoryResponse:
        """
        Получить категорию по ID
        """
        try:
            category = await self.category_repository.get_category(category_id)
            return PlantCategoryResponse.model_validate(category)
        except Exception as e:
            self._log_error(f"Ошибка при получении категории с ID {category_id}", e)
            raise NotFoundError("PlantCategory", category_id)
    
    async def create_category(self, category_data: PlantCategoryCreate) -> PlantCategoryResponse:
        """
        Создать новую категорию растений
        """
        try:
            # Если указан parent_id, проверяем что родительская категория существует
            if category_data.parent_id is not None:
                try:
                    await self.category_repository.get_category(category_data.parent_id)
                except Exception:
                    raise ValidationError(f"Родительская категория с ID {category_data.parent_id} не найдена")
            
            # Проверяем, что категория с таким именем еще не существует
            existing_category = await self.category_repository.get_by_field_ilike("name", category_data.name)
            if existing_category:
                raise ValidationError(f"Категория с именем '{category_data.name}' уже существует")
            
            # Создаем категорию
            create_data = category_data.model_dump()
            category = await self.category_repository.create(create_data)
            
            return PlantCategoryResponse.model_validate(category)
        except ValidationError:
            raise
        except Exception as e:
            self._log_error("Ошибка при создании категории растений", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось создать категорию: {str(e)}")
    
    async def update_category(self, category_id: int, category_data: PlantCategoryUpdate) -> PlantCategoryResponse:
        """
        Обновить категорию растений
        """
        try:
            # Проверяем, что категория существует
            await self.category_repository.get_category(category_id)
            
            # Если меняется имя, проверяем, что оно не конфликтует с другими категориями
            if category_data.name:
                existing_category = await self.category_repository.get_category_by_name(category_data.name)
                if existing_category and existing_category.id != category_id:
                    raise ValidationError(f"Категория с именем '{category_data.name}' уже существует")
            
            # Если меняется родительская категория, проверяем, что она существует
            if category_data.parent_id is not None:
                # Нельзя установить категорию как родителя самой себя
                if category_data.parent_id == category_id:
                    raise ValidationError("Категория не может быть родителем самой себя")
                
                # Проверяем, что родительская категория существует
                try:
                    await self.category_repository.get_category(category_data.parent_id)
                except Exception:
                    raise ValidationError(f"Родительская категория с ID {category_data.parent_id} не найдена")
            
            # Обновляем категорию
            update_data = category_data.model_dump(exclude_unset=True)
            category = await self.category_repository.update(category_id, update_data)
            
            return PlantCategoryResponse.model_validate(category)
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении категории с ID {category_id}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось обновить категорию: {str(e)}")
    
    async def delete_category(self, category_id: int) -> bool:
        """
        Удалить категорию растений
        """
        try:
            # Проверяем, что категория существует
            await self.category_repository.get_category(category_id)
            
            # Удаляем категорию
            result = await self.category_repository.delete(category_id)
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении категории с ID {category_id}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось удалить категорию: {str(e)}")
    
    async def get_plants_by_category(self, category_id: int, skip: int = 0, limit: int = 20) -> PlantListResponse:
        """
        Получить растения по категории
        """
        try:
            # Проверяем, что категория существует
            await self.category_repository.get_category(category_id)
            
            # Получаем растения в категории
            plants = await self.category_repository.get_plants_by_category(category_id, skip, limit)
            
            # Получаем общее количество растений в категории
            total = await self.category_repository.count_plants_by_category(category_id)
            
            # Преобразуем результаты в схему ответа
            items = [PlantResponse.model_validate(plant) for plant in plants]
            
            # Расчет количества страниц
            pages = (total + limit - 1) // limit if limit > 0 else 0
            
            # Формируем ответ с пагинацией
            return PlantListResponse(
                items=items,
                total=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                size=limit,
                pages=pages
            )
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении растений для категории с ID {category_id}", e)
            raise ValidationError(f"Не удалось получить растения по категории: {str(e)}") 