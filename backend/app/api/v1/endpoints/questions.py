from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse

from app.api.common.security import get_current_user
from app.application.services.question_service import QuestionService
from app.domain.models.user import User
from app.domain.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionDetailResponse,
    QuestionListResponse
)
from app.domain.schemas.vote import QuestionVoteCreate as QuestionVote
from app.application.services.base import NotFoundError, ValidationError, AuthorizationError
from app.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=QuestionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый вопрос"""
    question_service = QuestionService(db=db)
    return await question_service.create_question(data=question, author_id=current_user.id)


@router.get("/", response_model=QuestionListResponse)
async def get_questions(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по вопросам"),
    # Убрать эту строку:
    # tag: Optional[str] = Query(None, description="Фильтр по тегу"),
    plant_id: Optional[int] = Query(None, description="Фильтр по ID растения"),
    author_id: Optional[int] = Query(None, description="Фильтр по ID автора"),
    is_solved: Optional[bool] = Query(None, description="Фильтр по статусу решения"),
    sort_by: str = Query("created_at", description="Поле для сортировки"),
    sort_order: str = Query("desc", description="Порядок сортировки (asc/desc)"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить список вопросов с пагинацией и фильтрацией"""
    question_service = QuestionService(db=db)
    
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    questions, total = await question_service.get_questions(
        skip=skip,
        limit=per_page,
        search=search,
        # Убрать эту строку:
        # tag=tag,
        plant_id=plant_id,
        author_id=author_id,
        is_solved=is_solved,
        sort_by=sort_by,
        sort_order=sort_order,
        user_id=current_user.id if current_user else None
    )
    return {
        "items": questions,
        "total": total,
        "page": page,
        "size": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@router.get("/{question_id}", response_model=QuestionDetailResponse)
async def get_question(
    question_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить один вопрос с деталями"""
    question_service = QuestionService(db=db)
    return await question_service.get_question(
        question_id=question_id,
        user_id=current_user.id if current_user else None
    )

@router.put("/{question_id}", response_model=QuestionDetailResponse)
async def update_question(
    question_id: int,
    question_update: QuestionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить вопрос"""
    question_service = QuestionService(db=db)
    return await question_service.update_question(
        question_id=question_id,
        data=question_update,
        user_id=current_user.id
    )

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить вопрос"""
    question_service = QuestionService(db=db)
    result = await question_service.delete_question(
        question_id=question_id,
        user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вопрос с ID {question_id} не найден"
        )
    return None

@router.post("/{question_id}/vote", response_model=QuestionDetailResponse)
async def vote_for_question(
    question_id: int,
    vote: QuestionVote,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Проголосовать за вопрос (за/против)"""
    question_service = QuestionService(db=db)
    return await question_service.vote_for_question(
        question_id=question_id,
        vote_data=vote,
        user_id=current_user.id
    ) 


router.get("/by-plant/{plant_id}", response_model=QuestionListResponse)
async def get_questions_by_plant(
    plant_id: int,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=50, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по вопросам"),
    is_solved: Optional[bool] = Query(None, description="Фильтр по статусу решения"),
    sort_by: str = Query("created_at", description="Поле для сортировки"),
    sort_order: str = Query("desc", description="Порядок сортировки (asc/desc)"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить вопросы по конкретному растению"""
    question_service = QuestionService(db=db)
    
    # Расчет skip из page и per_page
    skip = (page - 1) * per_page
    
    questions, total = await question_service.get_questions(
        skip=skip,
        limit=per_page,
        search=search,
        plant_id=plant_id,  # Фильтр по ID растения
        is_solved=is_solved,
        sort_by=sort_by,
        sort_order=sort_order,
        user_id=current_user.id if current_user else None
    )
    return {
        "items": questions,
        "total": total,
        "page": page,
        "size": per_page,
        "pages": (total + per_page - 1) // per_page
    }