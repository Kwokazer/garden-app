from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import (BaseService, NotFoundError,
                                           ValidationError)
from app.domain.models.plant_category import PlantCategory
from app.domain.schemas.plant_category import (PlantCategoryCreate,
                                              PlantCategoryResponse,
                                              PlantCategoryUpdate)
from app.domain.schemas.plant import (PlantListResponse,
                                      PlantResponse)
from app.infrastructure.database.repositories import (
    PlantCategoryRepository, PlantRepository)
from app.infrastructure.cache.plant_cache import PlantCache


class PlantCategoryService(BaseService):
    """
    Сервис для работы с категориями растений
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCache] = None):
        super().__init__()
        self.session = session
        self.category_repository = PlantCategoryRepository(session)
        self.plant_repository = PlantRepository(session)
        self.plant_cache = plant_cache
    
    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[PlantCategoryResponse]:
        """
        Получить список категорий растений
        """
        # Пытаемся получить данные из кэша, если кэш доступен
        cache_key = f"categories:list:{skip}:{limit}"
        cached_data = None
        
        if self.plant_cache:
            cached_data = await self.plant_cache.redis.get(cache_key)
            if cached_data:
                self._log_info(f"Получены категории из кэша: {cache_key}")
                return [PlantCategoryResponse.model_validate(category) for category in cached_data]
        
        # Если данных нет в кэше, получаем из базы
        categories = await self.category_repository.get_categories(skip, limit)
        result = [PlantCategoryResponse.model_validate(category) for category in categories]
        
        # Сохраняем в кэш, если он доступен
        if self.plant_cache:
            data_to_cache = [category.model_dump() for category in result]
            await self.plant_cache.redis.set(cache_key, data_to_cache, expire=3600)  # Кэш на 1 час
            self._log_info(f"Сохранены категории в кэш: {cache_key}")
            
        return result
    
    async def get_category(self, category_id: int) -> PlantCategoryResponse:
        """
        Получить категорию по ID
        """
        try:
            category = await self.category_repository.get_category(category_id)
            if not category:
                raise NotFoundError("PlantCategory", category_id)
            return PlantCategoryResponse.model_validate(category)
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении категории с ID {category_id}", e)
            raise ValidationError(f"Не удалось получить категорию: {str(e)}")
    
    async def create_category(self, category_data: PlantCategoryCreate) -> PlantCategoryResponse:
        """
        Создать новую категорию растений
        """
        try:
            # Проверяем, что категория с таким названием еще не существует
            existing_category = await self.category_repository.get_category_by_name(category_data.name)
            if existing_category:
                raise ValidationError(f"Категория с названием '{category_data.name}' уже существует")
            
            # Создаем категорию
            create_data = category_data.model_dump()
            category = await self.category_repository.create(create_data)
            
            # Инвалидируем кэш категорий
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша категорий
                pass
            
            return PlantCategoryResponse.model_validate(category)
        except ValidationError:
            raise
        except Exception as e:
            self._log_error("Ошибка при создании категории", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось создать категорию: {str(e)}")
    
    async def update_category(self, category_id: int, category_data: PlantCategoryUpdate) -> PlantCategoryResponse:
        """
        Обновить категорию растений
        """
        try:
            # Проверяем, что категория существует
            existing_category = await self.category_repository.get_category(category_id)
            if not existing_category:
                raise NotFoundError("PlantCategory", category_id)
            
            # Если новое имя указано и оно отличается от старого, проверяем, что оно не конфликтует с другими категориями
            if category_data.name is not None and category_data.name != existing_category.name:
                name_check = await self.category_repository.get_category_by_name(category_data.name)
                if name_check:
                    raise ValidationError(f"Категория с названием '{category_data.name}' уже существует")
            
            # Обновляем категорию
            update_data = category_data.model_dump(exclude_unset=True)
            category = await self.category_repository.update(category_id, update_data)
            
            # Инвалидируем кэш категорий
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша категорий
                pass
            
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
            existing_category = await self.category_repository.get_category(category_id)
            if not existing_category:
                raise NotFoundError("PlantCategory", category_id)
            
            # Проверяем, что нет растений в этой категории
            plant_count = await self.category_repository.count_plants_in_category(category_id)
            if plant_count > 0:
                raise ValidationError(f"Невозможно удалить категорию, так как она содержит {plant_count} растений")
            
            # Удаляем категорию
            result = await self.category_repository.delete(category_id)
            
            # Инвалидируем кэш категорий
            if self.plant_cache:
                # В реальном проекте здесь был бы код для инвалидации всех ключей кэша категорий
                pass
            
            return result
        except NotFoundError:
            raise
        except ValidationError:
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
            existing_category = await self.category_repository.get_category(category_id)
            if not existing_category:
                raise NotFoundError("PlantCategory", category_id)
            
            # Пытаемся получить данные из кэша, если кэш доступен
            if self.plant_cache:
                cached_result = await self.plant_cache.get_category_plants(category_id, skip, limit)
                if cached_result:
                    self._log_info(f"Получены растения для категории {category_id} из кэша")
                    return cached_result
            
            # Если данных нет в кэше, получаем из базы
            plants = await self.category_repository.get_plants_by_category(category_id, skip, limit)
            total = await self.category_repository.count_plants_by_category(category_id)
            
            # Преобразуем результаты в схему ответа
            items = [PlantResponse.model_validate(plant) for plant in plants]
            
            # Расчет количества страниц
            pages = (total + limit - 1) // limit if limit > 0 else 0
            
            # Формируем ответ с пагинацией
            result = PlantListResponse(
                items=items,
                total_items=total,
                page=(skip // limit) + 1 if limit > 0 else 1,
                per_page=limit,
                total_pages=pages
            )
            
            # Сохраняем результат в кэш, если кэш доступен
            if self.plant_cache:
                await self.plant_cache.set_category_plants(category_id, result, skip, limit)
                self._log_info(f"Сохранены растения для категории {category_id} в кэш")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении растений для категории {category_id}", e)
            raise ValidationError(f"Не удалось получить растения по категории: {str(e)}") 