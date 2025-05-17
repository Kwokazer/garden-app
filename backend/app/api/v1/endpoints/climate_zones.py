from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.application.services.base import NotFoundError, ValidationError
from app.application.services.climate_zone_service import ClimateZoneService
from app.domain.schemas.climate_zone import (ClimateZoneCreate, ClimateZoneResponse,
                                           ClimateZoneUpdate)
from app.domain.schemas.plant import PlantListResponse

router = APIRouter()

# Зависимости для сервисов
async def get_climate_zone_service(session: AsyncSession = Depends(get_db)) -> ClimateZoneService:
    return ClimateZoneService(session)


@router.get("/", response_model=List[ClimateZoneResponse])
async def get_climate_zones(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(100, ge=1, le=100, description="Количество записей на странице"),
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Получить список климатических зон
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    zones = await climate_zone_service.get_climate_zones(skip=skip, limit=per_page)
    return zones


@router.get("/{id}", response_model=ClimateZoneResponse)
async def get_climate_zone(
    id: int = Path(..., ge=1, description="ID климатической зоны"),
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Получить климатическую зону по ID
    """
    try:
        zone = await climate_zone_service.get_climate_zone(id)
        return zone
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/", response_model=ClimateZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_climate_zone(
    zone_data: ClimateZoneCreate,
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Создать новую климатическую зону
    """
    try:
        zone = await climate_zone_service.create_climate_zone(zone_data)
        return zone
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{id}", response_model=ClimateZoneResponse)
async def update_climate_zone(
    id: int = Path(..., ge=1, description="ID климатической зоны"),
    zone_data: ClimateZoneUpdate = None,
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Обновить климатическую зону
    """
    try:
        zone = await climate_zone_service.update_climate_zone(id, zone_data)
        return zone
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_climate_zone(
    id: int = Path(..., ge=1, description="ID климатической зоны"),
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Удалить климатическую зону
    """
    try:
        await climate_zone_service.delete_climate_zone(id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{id}/plants", response_model=PlantListResponse)
async def get_plants_by_climate_zone(
    id: int = Path(..., ge=1, description="ID климатической зоны"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    climate_zone_service: ClimateZoneService = Depends(get_climate_zone_service)
):
    """
    Получить растения по климатической зоне
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    try:
        plants = await climate_zone_service.get_plants_by_climate_zone(id, skip=skip, limit=per_page)
        return plants
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 