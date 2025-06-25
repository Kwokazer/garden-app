# backend/app/api/v1/endpoints/answers.py
from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.answer_service import AnswerService
from app.application.services.base import NotFoundError, AuthorizationError, ValidationError
from app.api.common.security import get_current_user, optional_current_user
from app.domain.models.user import User
from app.domain.schemas.answer import AnswerCreate, AnswerResponse, AnswerUpdate
from app.domain.schemas.vote import AnswerVoteCreate as AnswerVote
from app.infrastructure.database import get_db
from app.domain.schemas.question import QuestionDetailResponse

router = APIRouter()

@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer: AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создать новый ответ на вопрос"""
    service = AnswerService(db)
    return await service.create_answer(data=answer, author_id=current_user.id)

@router.put("/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    answer_id: int,
    answer_update: AnswerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить ответ"""
    service = AnswerService(db)
    return await service.update_answer(
        answer_id=answer_id,
        data=answer_update,
        user_id=current_user.id
    )

@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удалить ответ"""
    service = AnswerService(db)
    result = await service.delete_answer(
        answer_id=answer_id,
        user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ответ с ID {answer_id} не найден"
        )
    return None

@router.post("/{answer_id}/accept", response_model=AnswerResponse)
async def accept_answer(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Отметить ответ как принятый"""
    service = AnswerService(db)
    return await service.mark_answer_as_accepted(
        answer_id=answer_id,
        user_id=current_user.id
    )

@router.post("/{answer_id}/vote", response_model=AnswerResponse)
async def vote_for_answer(
    answer_id: int,
    vote: AnswerVote,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Проголосовать за ответ (за/против)"""
    service = AnswerService(db)
    return await service.vote_for_answer(
        answer_id=answer_id,
        vote_data=vote,
        user_id=current_user.id
    )

# ИСПРАВЛЕНО: Изменен параметр с 'id' на 'answer_id'
@router.post("/{answer_id}/unaccept", response_model=QuestionDetailResponse)
async def unaccept_answer(
    answer_id: int = Path(..., description="ID ответа"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Отменить принятие ответа как решение вопроса.
    
    - **answer_id**: ID ответа
    """
    service = AnswerService(db)
    try:
        return await service.unaccept_answer(answer_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось отменить принятие ответа: {str(e)}"
        )