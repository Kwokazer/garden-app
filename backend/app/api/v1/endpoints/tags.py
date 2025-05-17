from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.tag import TagResponse as TagInDB
from app.infrastructure.database import get_db
from app.infrastructure.database.repositories import TagRepository
from app.application.services.base import NotFoundError, ValidationError

router = APIRouter()

@router.get("/", response_model=List[TagInDB])
async def get_tags(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все теги с пагинацией
    """
    try:
        tag_repo = TagRepository(db)
        # Расчет skip из page и per_page
        skip = (page - 1) * per_page
        tags = await tag_repo.get_all_tags(skip=skip, limit=per_page)
        return tags
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении тегов: {str(e)}"
        )

@router.get("/search", response_model=List[TagInDB])
async def search_tags(
    query: str = Query(..., description="Строка поиска"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество результатов"),
    db: AsyncSession = Depends(get_db)
):
    """
    Поиск тегов по части имени
    """
    try:
        tag_repo = TagRepository(db)
        tags = await tag_repo.search_tags(query, limit)
        return tags
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске тегов: {str(e)}"
        ) 