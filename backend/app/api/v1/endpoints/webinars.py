# backend/app/api/v1/endpoints/webinars.py
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common.security import get_current_active_user, check_role
from app.application.services.base import NotFoundError, ValidationError, AuthorizationError
from app.application.services.webinar_service import WebinarService
from app.application.services.jitsi_service import JitsiService
from app.domain.models import User
from app.domain.schemas.webinar import (
    WebinarCreate, WebinarUpdate, WebinarResponse, WebinarListResponse,
    WebinarFilterParams, WebinarParticipantCreate, WebinarParticipantUpdate,
    JitsiTokenRequest, JitsiTokenResponse,
    WebinarStatusEnum, ParticipantRoleEnum
)
from app.infrastructure.database import get_db

router = APIRouter()

# Зависимости для сервисов
async def get_webinar_service(db: AsyncSession = Depends(get_db)) -> WebinarService:
    """Получение сервиса вебинаров"""
    return WebinarService(db)

async def get_jitsi_service() -> JitsiService:
    """Получение сервиса Jitsi"""
    return JitsiService()

# Функция для проверки прав на создание вебинаров
def check_webinar_host_role():
    """Проверяет, что пользователь может быть ведущим вебинара"""
    async def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not (current_user.has_role("admin") or current_user.has_role("plant_expert")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администраторы и эксперты могут создавать вебинары"
            )
        return current_user
    return role_dependency

# CRUD операции для вебинаров
@router.get("/", response_model=WebinarListResponse)
async def get_webinars(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    title: Optional[str] = Query(None, description="Поиск по названию"),
    host_id: Optional[int] = Query(None, description="Фильтр по ID ведущего"),
    status: Optional[WebinarStatusEnum] = Query(None, description="Фильтр по статусу"),
    is_public: Optional[bool] = Query(None, description="Фильтр по публичности"),
    plant_topic_id: Optional[int] = Query(None, description="Фильтр по теме растения"),
    date_from: Optional[datetime] = Query(None, description="Фильтр по дате начала"),
    date_to: Optional[datetime] = Query(None, description="Фильтр по дате окончания"),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarListResponse:
    """
    Получить список вебинаров с поддержкой фильтрации и пагинации.
    """
    filters = WebinarFilterParams(
        title=title,
        host_id=host_id,
        status=status,
        is_public=is_public,
        plant_topic_id=plant_topic_id,
        date_from=date_from,
        date_to=date_to
    )
    
    try:
        result = await webinar_service.get_webinars(filters, page, per_page)
        return WebinarListResponse(**result)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{webinar_id}", response_model=WebinarResponse)
async def get_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarResponse:
    """
    Получить детальную информацию о вебинаре по ID.
    """
    try:
        webinar = await webinar_service.get_webinar(webinar_id)
        return WebinarResponse.model_validate(webinar)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )

@router.post("/", response_model=WebinarResponse, status_code=status.HTTP_201_CREATED)
async def create_webinar(
    webinar_data: WebinarCreate,
    current_user: User = Depends(check_webinar_host_role()),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarResponse:
    """
    Создать новый вебинар. Доступно только администраторам и экспертам.
    """
    try:
        webinar = await webinar_service.create_webinar(webinar_data, current_user)
        return WebinarResponse.model_validate(webinar)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.put("/{webinar_id}", response_model=WebinarResponse)
async def update_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    webinar_data: WebinarUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarResponse:
    """
    Обновить существующий вебинар. Доступно только ведущему и администраторам.
    """
    try:
        webinar = await webinar_service.update_webinar(webinar_id, webinar_data, current_user)
        return WebinarResponse.model_validate(webinar)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.delete("/{webinar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> None:
    """
    Удалить вебинар. Доступно только ведущему и администраторам.
    """
    try:
        await webinar_service.delete_webinar(webinar_id, current_user)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

# Управление участниками
@router.post("/{webinar_id}/participants")
async def add_participant(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    participant_data: WebinarParticipantCreate = ...,
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
):
    """
    Добавить участника в вебинар. Доступно только ведущему и администраторам.
    """
    try:
        # Проверяем права на управление участниками
        webinar = await webinar_service.get_webinar(webinar_id)
        if not (current_user.has_role("admin") or current_user.id == webinar.host_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только ведущие и администраторы могут добавлять участников"
            )
        
        participant = await webinar_service.add_participant(
            webinar_id, 
            participant_data.user_id, 
            participant_data.role
        )
        return {"message": "Участник добавлен", "participant_id": participant.id}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )

@router.delete("/{webinar_id}/participants/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    user_id: int = Path(..., ge=1, description="ID пользователя"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> None:
    """
    Удалить участника из вебинара. Доступно только ведущему и администраторам.
    """
    try:
        # Проверяем права на управление участниками
        webinar = await webinar_service.get_webinar(webinar_id)
        if not (current_user.has_role("admin") or current_user.id == webinar.host_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только ведущие и администраторы могут удалять участников"
            )
        
        await webinar_service.remove_participant(webinar_id, user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )

# Регистрация на вебинар
@router.post("/{webinar_id}/register")
async def register_for_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
):
    """
    Зарегистрироваться на вебинар. Добавляет пользователя в список участников.
    Доступно для вебинаров со статусом SCHEDULED.
    """
    try:
        participant = await webinar_service.register_for_webinar(webinar_id, current_user)
        return {
            "message": "Вы успешно зарегистрированы на вебинар",
            "participant_id": participant.id,
            "webinar_id": webinar_id
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

# Отмена регистрации на вебинар
@router.delete("/{webinar_id}/unregister", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> None:
    """
    Отменить регистрацию на вебинар (удалить себя из списка участников).
    """
    try:
        await webinar_service.unregister_from_webinar(webinar_id, current_user)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден или вы не зарегистрированы на него"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Присоединение к вебинару
@router.post("/{webinar_id}/join")
async def join_webinar(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
):
    """
    Присоединиться к вебинару и получить данные для подключения к Jitsi.
    """
    try:
        connection_data = await webinar_service.join_webinar(webinar_id, current_user)
        return connection_data
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

# Jitsi интеграция
@router.post("/{webinar_id}/jitsi-token", response_model=JitsiTokenResponse)
async def get_jitsi_token(
    webinar_id: int = Path(..., ge=1, description="ID вебинара"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service),
    jitsi_service: JitsiService = Depends(get_jitsi_service)
) -> JitsiTokenResponse:
    """
    Получить JWT токен для подключения к Jitsi Meet.
    """
    try:
        webinar = await webinar_service.get_webinar(webinar_id)

        # Проверяем доступ к вебинару
        if not webinar.is_public and current_user.id != webinar.host_id:
            # Проверяем, что пользователь является участником
            is_participant = any(
                p.user_id == current_user.id for p in webinar.participants
            )
            if not is_participant:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Доступ к приватному вебинару запрещен"
                )

        jwt_data = jitsi_service.generate_jwt_token(current_user, webinar)

        return JitsiTokenResponse(
            token=jwt_data["token"],
            room_name=jwt_data["room_name"],
            jitsi_url=jwt_data["jitsi_url"],
            expires_at=jwt_data["expires_at"]
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вебинар с ID {webinar_id} не найден"
        )



# Дополнительные эндпоинты
@router.get("/my/hosted", response_model=WebinarListResponse)
async def get_my_hosted_webinars(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarListResponse:
    """
    Получить список вебинаров, которые ведет текущий пользователь.
    """
    filters = WebinarFilterParams(host_id=current_user.id)

    try:
        result = await webinar_service.get_webinars(filters, page, per_page)
        return WebinarListResponse(**result)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/my/participating", response_model=WebinarListResponse)
async def get_my_participating_webinars(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    current_user: User = Depends(get_current_active_user),
    webinar_service: WebinarService = Depends(get_webinar_service)
) -> WebinarListResponse:
    """
    Получить список вебинаров, в которых участвует текущий пользователь.
    """
    try:
        result = await webinar_service.get_participating_webinars(current_user, page, per_page)
        return WebinarListResponse(**result)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
