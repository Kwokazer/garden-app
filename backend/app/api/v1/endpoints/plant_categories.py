from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import NotFoundError, ValidationError
from app.application.services.plant_category_service import PlantCategoryService
from app.domain.schemas.plant_category import (PlantCategoryCreate, PlantCategoryResponse, PlantCategoryUpdate)
from app.domain.schemas.plant import PlantListResponse
from app.infrastructure.database import get_db
from app.infrastructure.cache.plant_cache import PlantCache
from app.infrastructure.cache.redis_service import RedisService

router = APIRouter()

# Зависимости для сервисов
async def get_redis_service() -> RedisService:
    redis_service = RedisService()
    await redis_service.connect()
    try:
        yield redis_service
    finally:
        await redis_service.close()

async def get_plant_cache(redis_service: RedisService = Depends(get_redis_service)) -> PlantCache:
    return PlantCache(redis_service)

async def get_category_service(
    session: AsyncSession = Depends(get_db),
    plant_cache: Optional[PlantCache] = Depends(get_plant_cache)
) -> PlantCategoryService:
    return PlantCategoryService(session, plant_cache)

# Эндпоинты для работы с категориями растений
@router.get("/", response_model=List[PlantCategoryResponse])
async def get_categories(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(100, ge=1, le=1000, description="Количество записей на странице"),
    category_service: PlantCategoryService = Depends(get_category_service)
) -> List[PlantCategoryResponse]:
    """
    Получить список категорий растений.
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    return await category_service.get_categories(skip=skip, limit=per_page)

@router.get("/{id}", response_model=PlantCategoryResponse)
async def get_category(
    id: int = Path(..., ge=1, description="ID категории"),
    category_service: PlantCategoryService = Depends(get_category_service)
) -> PlantCategoryResponse:
    """
    Получить детальную информацию о категории растений по ID.
    """
    try:
        return await category_service.get_category(id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID {id} не найдена"
        )

@router.post("/", response_model=PlantCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: PlantCategoryCreate,
    category_service: PlantCategoryService = Depends(get_category_service)
) -> PlantCategoryResponse:
    """
    Создать новую категорию растений.
    """
    try:
        return await category_service.create_category(category_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=PlantCategoryResponse)
async def update_category(
    id: int = Path(..., ge=1, description="ID категории"),
    category_data: PlantCategoryUpdate = ...,
    category_service: PlantCategoryService = Depends(get_category_service)
) -> PlantCategoryResponse:
    """
    Обновить существующую категорию растений.
    """
    try:
        return await category_service.update_category(id, category_data)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID {id} не найдена"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    id: int = Path(..., ge=1, description="ID категории"),
    category_service: PlantCategoryService = Depends(get_category_service)
) -> None:
    """
    Удалить категорию растений.
    """
    try:
        await category_service.delete_category(id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID {id} не найдена"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{id}/plants", response_model=PlantListResponse)
async def get_plants_by_category(
    id: int = Path(..., ge=1, description="ID категории"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    category_service: PlantCategoryService = Depends(get_category_service)
) -> PlantListResponse:
    """
    Получить список растений, принадлежащих указанной категории.
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    try:
        return await category_service.get_plants_by_category(
            category_id=id,
            skip=skip,
            limit=per_page
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Категория с ID {id} не найдена"
        ) 