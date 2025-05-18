import json
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
from app.domain.schemas.plant_image import PlantImageCreate, PlantImageResponse
from app.infrastructure.database.repositories import (
    PlantRepository, PlantCategoryRepository, ClimateZoneRepository)
from app.infrastructure.cache.plant_cache import PlantCacheService

class PlantService(BaseService):
    """
    Сервис для работы с растениями
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCacheService] = None):
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
            items = []
            for plant in plants:
                # Обрабатываем JSON поля для каждого растения
                json_fields = self._process_plant_json_fields(plant)
                
                # Создаем словарь для PlantResponse
                plant_dict = {}
                
                # Копируем все простые поля из модели
                for field_name in PlantResponse.model_fields.keys():
                    if hasattr(plant, field_name) and field_name not in json_fields:
                        plant_dict[field_name] = getattr(plant, field_name)
                
                # Добавляем обработанные JSON поля
                plant_dict.update(json_fields)
                
                # Обрабатываем связанные объекты
                if plant.categories:
                    plant_dict['categories'] = [
                        {'id': cat.id, 'name': cat.name} for cat in plant.categories
                    ]
                else:
                    plant_dict['categories'] = []
                
                if plant.climate_zones:
                    plant_dict['climate_zones'] = [
                        {'id': zone.id, 'name': zone.name, 'zone_number': zone.zone_number} 
                        for zone in plant.climate_zones
                    ]
                else:
                    plant_dict['climate_zones'] = []
                
                if plant.images:
                    plant_dict['images'] = [
                        {
                            'id': img.id,
                            'url': img.url,
                            'alt': img.alt,
                            'title': img.title,
                            'description': img.description,
                            'thumbnail_url': img.thumbnail_url,
                            'is_primary': img.is_primary
                        } for img in plant.images
                    ]
                else:
                    plant_dict['images'] = []
                
                if plant.tags:
                    plant_dict['tags'] = [
                        {'id': tag.id, 'name': tag.name} for tag in plant.tags
                    ]
                else:
                    plant_dict['tags'] = []
                
                items.append(PlantResponse.model_validate(plant_dict))
            
            # Расчет количества страниц
            pages = (total + limit - 1) // limit if limit > 0 else 0
            
            # Формируем ответ с пагинацией - ИСПРАВЛЕННЫЕ ПОЛЯ
            result = PlantListResponse(
                items=items,
                total_items=total,  # Изменено с total
                total_pages=pages,  # Изменено с pages
                page=(skip // limit) + 1 if limit > 0 else 1,
                per_page=limit     # Изменено с size
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
            
            # Обрабатываем JSON поля
            json_fields = self._process_plant_json_fields(plant)
            
            # Создаем словарь для PlantResponse, объединяя данные модели и обработанные JSON поля
            plant_dict = {}
            
            # Копируем все простые поля из модели
            for field_name in PlantResponse.model_fields.keys():
                if hasattr(plant, field_name) and field_name not in json_fields:
                    plant_dict[field_name] = getattr(plant, field_name)
            
            # Добавляем обработанные JSON поля
            plant_dict.update(json_fields)
            
            # Обрабатываем связанные объекты
            if plant.categories:
                plant_dict['categories'] = [
                    {'id': cat.id, 'name': cat.name} for cat in plant.categories
                ]
            else:
                plant_dict['categories'] = []
            
            if plant.climate_zones:
                plant_dict['climate_zones'] = [
                    {'id': zone.id, 'name': zone.name, 'zone_number': zone.zone_number} 
                    for zone in plant.climate_zones
                ]
            else:
                plant_dict['climate_zones'] = []
            
            if plant.images:
                plant_dict['images'] = [
                    {
                        'id': img.id,
                        'url': img.url,
                        'alt': img.alt,
                        'title': img.title,
                        'description': img.description,
                        'thumbnail_url': img.thumbnail_url,
                        'is_primary': img.is_primary
                    } for img in plant.images
                ]
            else:
                plant_dict['images'] = []
            
            if plant.tags:
                plant_dict['tags'] = [
                    {'id': tag.id, 'name': tag.name} for tag in plant.tags
                ]
            else:
                plant_dict['tags'] = []
            
            # Создаем объект PlantResponse
            result = PlantResponse.model_validate(plant_dict)
            
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
    
    async def add_plant_image(self, plant_id: int, image_data: PlantImageCreate) -> PlantImageResponse:
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
    
    async def delete_plant_image(self, image_id: int) -> bool:
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
        
    
    def _process_plant_json_fields(self, plant: Plant) -> Dict[str, Any]:
        """Обрабатывает JSON поля растения для ответа API"""
        result = {}
        
        # Обработка care_tips
        if plant.care_tips:
            try:
                result['care_tips'] = json.loads(plant.care_tips) if isinstance(plant.care_tips, str) else plant.care_tips
            except (json.JSONDecodeError, TypeError):
                result['care_tips'] = []
        else:
            result['care_tips'] = []
        
        # Обработка common_problems  
        if plant.common_problems:
            try:
                result['common_problems'] = json.loads(plant.common_problems) if isinstance(plant.common_problems, str) else plant.common_problems
            except (json.JSONDecodeError, TypeError):
                result['common_problems'] = []
        else:
            result['common_problems'] = []
            
        # Обработка propagation_methods
        if plant.propagation_methods:
            try:
                result['propagation_methods'] = json.loads(plant.propagation_methods) if isinstance(plant.propagation_methods, str) else plant.propagation_methods
            except (json.JSONDecodeError, TypeError):
                result['propagation_methods'] = []
        else:
            result['propagation_methods'] = []
        
        return result