from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import NotFoundError, ValidationError
from app.application.services.plant_service import PlantService
from app.application.services.plant_search_service import PlantSearchService
from app.domain.schemas.plant import (PlantCreate, PlantFilterParams,
                                     PlantListResponse, PlantResponse, PlantUpdate)
from app.domain.schemas.plant_image import PlantImageCreate, PlantImageResponse
from app.infrastructure.database import get_db
from app.infrastructure.cache.plant_cache import PlantCacheService
from app.infrastructure.cache.redis_service import get_redis_service as get_redis_service_factory

router = APIRouter()

# Зависимости для сервисов
async def get_redis_service():
    """Получение Redis сервиса"""
    redis_service = await get_redis_service_factory()
    try:
        yield redis_service
    finally:
        await redis_service.close()

async def get_plant_cache(redis_service = Depends(get_redis_service)) -> PlantCacheService:
    """Получение кэша растений"""
    return PlantCacheService(redis_service)

async def get_plant_service(
    session: AsyncSession = Depends(get_db),
    plant_cache: Optional[PlantCacheService] = Depends(get_plant_cache)
) -> PlantService:
    """Получение сервиса растений"""
    return PlantService(session, plant_cache)

async def get_search_service(
    session: AsyncSession = Depends(get_db),
    plant_cache: Optional[PlantCacheService] = Depends(get_plant_cache)
) -> PlantSearchService:
    """Получение сервиса поиска растений"""
    return PlantSearchService(session, plant_cache)

# Эндпоинты для поиска растений
@router.get("/search", response_model=PlantListResponse)
async def get_plants_search(
    query: Optional[str] = Query(None, description="Строка поиска"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    name: Optional[str] = Query(None, description="Фильтр по имени растения"),
    category_id: Optional[int] = Query(None, description="Фильтр по ID категории"),
    climate_zone_id: Optional[int] = Query(None, description="Фильтр по ID климатической зоны"),
    plant_type: Optional[str] = Query(None, description="Фильтр по типу растения"),
    min_popularity: Optional[int] = Query(None, ge=0, description="Фильтр по минимальной популярности"),
    min_hardiness_zone: Optional[int] = Query(None, ge=1, le=13, description="Минимальная зона морозостойкости"),
    max_hardiness_zone: Optional[int] = Query(None, ge=1, le=13, description="Максимальная зона морозостойкости"),
    sort_by: Optional[str] = Query("name", description="Поле для сортировки"),
    sort_direction: Optional[str] = Query("asc", description="Направление сортировки (asc, desc)"),
    use_cache: bool = Query(True, description="Использовать ли кэширование результатов"),
    search_service: PlantSearchService = Depends(get_search_service)
) -> PlantListResponse:
    """
    Полнотекстовый поиск растений с поддержкой фильтрации и пагинации.
    
    - Текстовый поиск осуществляется по названию, научному названию и описанию растения
    - Результаты можно дополнительно фильтровать по различным параметрам
    - Поддерживается пагинация результатов
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    # Создаем объект с параметрами фильтрации
    filters = PlantFilterParams(
        name=name,
        category_id=category_id,
        climate_zone_id=climate_zone_id,
        plant_type=plant_type,
        min_popularity=min_popularity,
        min_hardiness_zone=min_hardiness_zone,
        max_hardiness_zone=max_hardiness_zone,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    try:
        return await search_service.get_plants(
            query=query,
            filters=filters,
            skip=skip,
            limit=per_page,
            use_cache=use_cache
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Эндпоинты для работы с растениями
@router.get("/", response_model=PlantListResponse)
async def get_plants(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    name: Optional[str] = Query(None, description="Фильтр по имени растения"),
    category_id: Optional[int] = Query(None, description="Фильтр по ID категории"),
    plant_type: Optional[str] = Query(None, description="Фильтр по типу растения"),
    min_popularity: Optional[int] = Query(None, ge=0, description="Фильтр по популярности"),
    climate_zone_id: Optional[int] = Query(None, description="Фильтр по ID климатической зоны"),
    min_climate_zone: Optional[int] = Query(None, ge=1, description="Фильтр по минимальной климатической зоне"),
    max_climate_zone: Optional[int] = Query(None, description="Фильтр по максимальной климатической зоне"),
    min_hardiness_zone: Optional[int] = Query(None, ge=1, le=13, description="Минимальная зона морозостойкости"),
    max_hardiness_zone: Optional[int] = Query(None, ge=1, le=13, description="Максимальная зона морозостойкости"),
    sort_by: Optional[str] = Query("name", description="Поле для сортировки (name, created_at, popularity)"),
    sort_direction: Optional[str] = Query("asc", description="Направление сортировки (asc, desc)"),
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantListResponse:
    """
    Получить список растений с поддержкой фильтрации и пагинации.
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    # Преобразуем plant_type в нижний регистр, если он указан
    if plant_type:
        plant_type = plant_type.lower()

    # Создаем объект с параметрами фильтрации
    filters = PlantFilterParams(
        name=name,
        category_id=category_id,
        plant_type=plant_type,
        min_popularity=min_popularity,
        climate_zone_id=climate_zone_id,
        min_climate_zone=min_climate_zone,
        max_climate_zone=max_climate_zone,
        min_hardiness_zone=min_hardiness_zone,
        max_hardiness_zone=max_hardiness_zone,
        sort_by=sort_by,
        sort_direction=sort_direction
    )
    
    return await plant_service.get_plants(skip=skip, limit=per_page, filters=filters)

@router.get("/{id}", response_model=PlantResponse)
async def get_plant(
    id: int = Path(..., ge=1, description="ID растения"),
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantResponse:
    """
    Получить детальную информацию о растении по ID.
    """
    try:
        return await plant_service.get_plant(id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Растение с ID {id} не найдено"
        )

@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant_data: PlantCreate,
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantResponse:
    """
    Создать новое растение.
    """
    try:
        return await plant_service.create_plant(plant_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=PlantResponse)
async def update_plant(
    id: int = Path(..., ge=1, description="ID растения"),
    plant_data: PlantUpdate = ...,
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantResponse:
    """
    Обновить существующее растение.
    """
    try:
        return await plant_service.update_plant(id, plant_data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Растение с ID {id} не найдено"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    id: int = Path(..., ge=1, description="ID растения"),
    plant_service: PlantService = Depends(get_plant_service)
) -> None:
    """
    Удалить растение.
    """
    try:
        await plant_service.delete_plant(id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Растение с ID {id} не найдено"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{id}/images", response_model=PlantImageResponse, status_code=status.HTTP_201_CREATED)
async def add_image_to_plant(
    id: int = Path(..., ge=1, description="ID растения"),
    image_data: PlantImageCreate = ...,
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantImageResponse:
    """
    Добавить изображение к растению.
    """
    try:
        return await plant_service.add_plant_image(id, image_data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Растение с ID {id} не найдено"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/images/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant_image(
    id: int = Path(..., ge=1, description="ID изображения"),
    plant_service: PlantService = Depends(get_plant_service)
) -> None:
    """
    Удалить изображение растения.
    """
    try:
        await plant_service.delete_plant_image(id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Изображение с ID {id} не найдено"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )