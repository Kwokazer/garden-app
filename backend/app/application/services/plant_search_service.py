import logging
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.services.base import BaseService, NotFoundError, ValidationError
from app.domain.models.plant import Plant
from app.domain.models.plant_category import PlantCategory, plant_to_category as plant_category
from app.domain.models.climate_zone import ClimateZone, plant_to_climate_zone as plant_climate_zone
from app.domain.schemas.plant import PlantFilterParams, PlantResponse, PlantListResponse
from app.infrastructure.cache.plant_cache import PlantCacheService  # Изменено с PlantCache

logger = logging.getLogger(__name__)

class PlantSearchService(BaseService):
    """
    Сервис для поиска и фильтрации растений
    """
    
    def __init__(self, session: AsyncSession, plant_cache: Optional[PlantCacheService] = None):
        super().__init__()
        self.session = session
        self.plant_cache = plant_cache
    
    async def get_plants(
        self,
        query: Optional[str] = None,
        filters: Optional[PlantFilterParams] = None,
        skip: int = 0,
        limit: int = 20,
        use_cache: bool = True
    ) -> PlantListResponse:
        """
        Получить список растений с возможностью поиска и фильтрации
        
        Args:
            query: Строка поиска (ищет в названии, научном названии и описании)
            filters: Параметры фильтрации
            skip: Смещение для пагинации
            limit: Количество элементов на странице
            use_cache: Использовать ли кэш
            
        Returns:
            PlantListResponse: Пагинированный список растений
        """
        # Конвертируем фильтры в словарь для использования в ключе кэша
        filters_dict = None
        if filters:
            filters_dict = filters.model_dump(exclude_unset=True)
            
        # Если включено использование кэша и есть кэш-сервис, пробуем получить из кэша
        if use_cache and self.plant_cache and not query:  # Не кэшируем результаты поиска
            cached_result = await self.plant_cache.get_plants_list(skip, limit, filters_dict)
            if cached_result:
                self._log_info(f"Данные получены из кэша для skip={skip}, limit={limit}, filters={filters_dict}")
                return cached_result
        
        # Выполняем поиск и фильтрацию
        plants, total = await self._execute_search(query, filters, skip, limit)
        
        # Преобразуем результаты в схему ответа
        items = [PlantResponse.model_validate(plant) for plant in plants]
        
        # Расчет количества страниц
        pages = (total + limit - 1) // limit if limit > 0 else 0
        current_page = (skip // limit) + 1 if limit > 0 else 1
        
        # Формируем ответ с пагинацией - ИСПРАВЛЕННЫЕ ПОЛЯ
        result = PlantListResponse(
            items=items,
            total_items=total,  # Изменено с total
            total_pages=pages,  # Изменено с pages
            page=current_page,
            per_page=limit     # Изменено с size
        )
        
        # Если кэширование включено и нет поискового запроса, сохраняем результат в кэш
        if use_cache and self.plant_cache and not query:
            await self.plant_cache.set_plants_list(result, skip, limit, filters_dict)
            self._log_info(f"Данные сохранены в кэш для skip={skip}, limit={limit}, filters={filters_dict}")
        
        return result
    
    async def _execute_search(
        self,
        query: Optional[str] = None,
        filters: Optional[PlantFilterParams] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Plant], int]:
        """
        Выполнить поиск с фильтрацией в базе данных
        
        Returns:
            Tuple[List[Plant], int]: Список растений и общее количество
        """
        # Создаем базовый запрос для получения растений
        base_query = (
            select(Plant)
            .options(
                selectinload(Plant.categories),
                selectinload(Plant.climate_zones),
                selectinload(Plant.images)
            )
        )
        
        # Создаем базовый запрос для подсчета общего количества
        count_query = select(func.count()).select_from(Plant)
        
        # Список условий фильтрации
        filter_conditions = []
        
        # Добавляем условие поиска, если указан поисковый запрос
        if query:
            search_query = f"%{query.lower()}%"
            search_condition = or_(
                func.lower(Plant.name).like(search_query),
                func.lower(Plant.latin_name).like(search_query),  # Изменено с scientific_name
                func.lower(Plant.description).like(search_query)
            )
            filter_conditions.append(search_condition)
        
        # Добавляем условия фильтрации, если указаны фильтры
        if filters:
            # Фильтр по имени
            if filters.name:
                name_filter = f"%{filters.name.lower()}%"
                filter_conditions.append(func.lower(Plant.name).like(name_filter))
            
            # Фильтр по категории
            if filters.category_id is not None:
                # Модифицируем запросы для добавления объединения с таблицей категорий
                base_query = base_query.join(
                    plant_category,
                    Plant.id == plant_category.c.plant_id
                )
                count_query = count_query.join(
                    plant_category,
                    Plant.id == plant_category.c.plant_id
                )
                filter_conditions.append(plant_category.c.category_id == filters.category_id)
            
            # Фильтр по климатической зоне
            if filters.climate_zone_id is not None:
                # Модифицируем запросы для добавления объединения с таблицей климатических зон
                base_query = base_query.join(
                    plant_climate_zone,
                    Plant.id == plant_climate_zone.c.plant_id
                )
                count_query = count_query.join(
                    plant_climate_zone,
                    Plant.id == plant_climate_zone.c.plant_id
                )
                filter_conditions.append(plant_climate_zone.c.climate_zone_id == filters.climate_zone_id)
            
            # Фильтр по типу растения
            if filters.plant_type:
                filter_conditions.append(Plant.plant_type == filters.plant_type)
            
            # Фильтр по минимальной популярности
            if filters.min_popularity is not None:
                filter_conditions.append(Plant.popularity_score >= filters.min_popularity)
            
            # Фильтр по зоне морозостойкости
            if filters.min_hardiness_zone is not None:
                filter_conditions.append(Plant.hardiness_zone_min >= filters.min_hardiness_zone)
            
            if filters.max_hardiness_zone is not None:
                filter_conditions.append(Plant.hardiness_zone_max <= filters.max_hardiness_zone)
        
        # Применяем все условия фильтрации
        if filter_conditions:
            combined_filter = and_(*filter_conditions)
            base_query = base_query.filter(combined_filter)
            count_query = count_query.filter(combined_filter)
        
        # Выполняем запрос для подсчета общего количества
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Применяем сортировку
        if filters and filters.sort_by:
            sort_column = None
            if filters.sort_by == "name":
                sort_column = Plant.name
            elif filters.sort_by == "created_at":
                sort_column = Plant.created_at
            elif filters.sort_by == "popularity":
                sort_column = Plant.popularity_score
            else:
                # По умолчанию сортируем по популярности и имени
                sort_column = Plant.popularity_score
            
            # Определяем направление сортировки
            if filters.sort_direction == "desc":
                sort_column = sort_column.desc()
            else:
                sort_column = sort_column.asc()
                
            base_query = base_query.order_by(sort_column, Plant.name)
        else:
            # По умолчанию сортируем по популярности (по убыванию) и имени
            base_query = base_query.order_by(Plant.popularity_score.desc(), Plant.name)
        
        # Применяем пагинацию
        base_query = base_query.offset(skip).limit(limit)
        
        # Выполняем запрос для получения растений
        result = await self.session.execute(base_query)
        plants = result.scalars().all()
        
        return plants, total
    
    async def get_categories(
        self, 
        query: Optional[str] = None,
        parent_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[PlantCategory], int]:
        """
        Получить список категорий растений с возможностью поиска и фильтрации
        
        Args:
            query: Строка поиска (ищет в названии и описании)
            parent_id: ID родительской категории для фильтрации
            skip: Смещение для пагинации
            limit: Количество элементов на странице
            
        Returns:
            Tuple[List[PlantCategory], int]: Список категорий и общее количество
        """
        # Создаем базовый запрос для получения категорий
        base_query = select(PlantCategory)
        
        # Создаем базовый запрос для подсчета общего количества
        count_query = select(func.count()).select_from(PlantCategory)
        
        # Список условий фильтрации
        filter_conditions = []
        
        # Добавляем условие поиска, если указан поисковый запрос
        if query:
            search_query = f"%{query.lower()}%"
            search_condition = or_(
                func.lower(PlantCategory.name).like(search_query),
                func.lower(PlantCategory.description).like(search_query)
            )
            filter_conditions.append(search_condition)
        
        # Фильтр по родительской категории
        if parent_id is not None:
            filter_conditions.append(PlantCategory.parent_id == parent_id)
        
        # Применяем все условия фильтрации
        if filter_conditions:
            combined_filter = and_(*filter_conditions)
            base_query = base_query.filter(combined_filter)
            count_query = count_query.filter(combined_filter)
        
        # Выполняем запрос для подсчета общего количества
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        # Применяем сортировку и пагинацию
        base_query = base_query.order_by(PlantCategory.name)
        base_query = base_query.offset(skip).limit(limit)
        
        # Выполняем запрос для получения категорий
        result = await self.session.execute(base_query)
        categories = result.scalars().all()
        
        return categories, total