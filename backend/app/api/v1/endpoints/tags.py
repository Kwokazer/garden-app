from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import NotFoundError, ValidationError
from app.application.services.tag_service import TagService
from app.domain.schemas.tag import (TagCreate, TagResponse, TagUpdate)
from app.infrastructure.database import get_db

router = APIRouter()

# Зависимости для сервисов
async def get_tag_service(session: AsyncSession = Depends(get_db)) -> TagService:
    return TagService(session)

@router.get("/", response_model=List[TagResponse])
async def get_tags(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по названию тега"),
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Получить список тегов с возможностью поиска
    """
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    if search:
        tags = await tag_service.search_tags(search, skip=skip, limit=per_page)
    else:
        tags = await tag_service.get_tags(skip=skip, limit=per_page)
    
    return tags

@router.get("/{id}", response_model=TagResponse)
async def get_tag(
    id: int = Path(..., ge=1, description="ID тега"),
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Получить тег по ID
    """
    try:
        tag = await tag_service.get_tag(id)
        return tag
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Создать новый тег
    """
    try:
        tag = await tag_service.create_tag(tag_data)
        return tag
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{id}", response_model=TagResponse)
async def update_tag(
    id: int = Path(..., ge=1, description="ID тега"),
    tag_data: TagUpdate = ...,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Обновить тег
    """
    try:
        tag = await tag_service.update_tag(id, tag_data)
        return tag
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
async def delete_tag(
    id: int = Path(..., ge=1, description="ID тега"),
    tag_service: TagService = Depends(get_tag_service)
):
    """
    Удалить тег
    """
    try:
        await tag_service.delete_tag(id)
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