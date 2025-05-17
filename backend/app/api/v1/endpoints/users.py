import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common.security import (check_permission, check_role,
                                     get_current_active_user,
                                     optional_current_user)
from app.application.dependencies import get_auth_service
from app.application.services.auth_service import AuthService
from app.domain.models.user import User
from app.domain.schemas.user import (AddRoleResponse, ChangeRoleRequest,
                                     RemoveRoleResponse, UserDetailResponse,
                                     UserListResponse, UserProfileResponse,
                                     UserResponse, UserUpdate)
from app.infrastructure.database import get_db
from app.infrastructure.database.repositories import (RoleRepository,
                                                      UserRepository)

# Создаем роутер с зависимостью AuthService на уровне роутера
router = APIRouter(dependencies=[Depends(get_auth_service)])
logger = logging.getLogger(__name__)

@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Получение информации о текущем пользователе
    
    Args:
        current_user: Текущий пользователь
        auth_service: Сервис аутентификации
    
    Returns:
        Dict[str, Any]: Информация о пользователе
    """
    # Получаем разрешения пользователя
    permissions = await auth_service.get_user_permissions(current_user.id)
    
    # Формируем ответ
    user_dict = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar_url": current_user.avatar_url,
        "bio": getattr(current_user, "bio", None),
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in current_user.roles],
        "permissions": [{"id": i+1, "name": perm, "description": None} for i, perm in enumerate(permissions)]
    }
    
    return user_dict

@router.get("/{id}", response_model=UserProfileResponse)
async def get_user_profile(
    id: int = Path(..., description="ID пользователя"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(optional_current_user)
) -> Dict[str, Any]:
    """
    Получение публичного профиля пользователя
    
    Args:
        id: ID пользователя
        db: Сессия базы данных
        current_user: Текущий пользователь (опционально)
    
    Returns:
        Dict[str, Any]: Публичный профиль пользователя
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {id} не найден"
        )
    
    # Проверка на приватность (для расширения в будущем)
    # Если пользователь просматривает себя или имеет роль администратора
    is_self = current_user and current_user.id == id
    is_admin = current_user and any(role.name == "admin" for role in current_user.roles) if current_user else False
    
    # Формируем базовый ответ
    profile = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar_url": user.avatar_url,
        "bio": getattr(user, "bio", None),
        "created_at": user.created_at
    }
    
    return profile

@router.get("/", response_model=UserListResponse)
@check_role("admin")
async def get_users(
    page: int = Query(1, description="Номер страницы", ge=1),
    size: int = Query(10, description="Размер страницы", ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получение списка всех пользователей (только для администраторов)
    
    Args:
        page: Номер страницы
        size: Размер страницы
        current_user: Текущий пользователь с ролью admin
        db: Сессия базы данных
    
    Returns:
        Dict[str, Any]: Список пользователей с пагинацией
    """
    user_repo = UserRepository(db)
    
    # Получаем пользователей с пагинацией
    users, total = await user_repo.get_all_paginated(page=page, page_size=size)
    
    # Формируем ответ
    items = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
            "bio": getattr(user, "bio", None),
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in user.roles]
        }
        items.append(user_dict)
    
    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Обновление данных текущего пользователя
    
    Args:
        user_data: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Dict[str, Any]: Обновленные данные пользователя
    
    Raises:
        HTTPException: При ошибке обновления данных
    """
    try:
        user_repo = UserRepository(db)
        
        # Проверка уникальности email и username
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Используем новый метод для проверки уникальности
        errors = await user_repo.check_unique_fields(
            email=update_data.get("email"),
            username=update_data.get("username"),
            user_id=current_user.id
        )
        
        if errors:
            # Выбираем первую ошибку для сообщения
            field, message = next(iter(errors.items()))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Обновляем данные пользователя
        updated_user = await user_repo.update(current_user.id, update_data)
        
        # Формируем ответ
        user_dict = {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "avatar_url": updated_user.avatar_url,
            "bio": getattr(updated_user, "bio", None),
            "is_active": updated_user.is_active,
            "is_verified": updated_user.is_verified,
            "created_at": updated_user.created_at,
            "updated_at": updated_user.updated_at,
            "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in updated_user.roles]
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении пользователя"
        )

@router.patch("/{id}", response_model=UserResponse)
@check_role("admin")
async def update_user(
    user_data: UserUpdate,
    id: int = Path(..., description="ID пользователя"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Обновление данных пользователя (только для администраторов)
    
    Args:
        user_data: Данные для обновления
        id: ID пользователя
        current_user: Текущий пользователь с ролью admin
        db: Сессия базы данных
    
    Returns:
        Dict[str, Any]: Обновленные данные пользователя
    
    Raises:
        HTTPException: При ошибке обновления данных
    """
    try:
        user_repo = UserRepository(db)
        
        # Проверяем существование пользователя
        user = await user_repo.get_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {id} не найден"
            )
        
        # Проверка уникальности email и username
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Используем новый метод для проверки уникальности
        errors = await user_repo.check_unique_fields(
            email=update_data.get("email"),
            username=update_data.get("username"),
            user_id=id
        )
        
        if errors:
            # Выбираем первую ошибку для сообщения
            field, message = next(iter(errors.items()))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Обновляем данные пользователя
        updated_user = await user_repo.update(id, update_data)
        
        # Формируем ответ
        user_dict = {
            "id": updated_user.id,
            "email": updated_user.email,
            "username": updated_user.username,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "avatar_url": updated_user.avatar_url,
            "bio": getattr(updated_user, "bio", None),
            "is_active": updated_user.is_active,
            "is_verified": updated_user.is_verified,
            "created_at": updated_user.created_at,
            "updated_at": updated_user.updated_at,
            "roles": [{"id": role.id, "name": role.name, "description": role.description} for role in updated_user.roles]
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении пользователя с ID {id}"
        )

@router.post("/{id}/roles", response_model=AddRoleResponse)
@check_role("admin")
async def add_role_to_user(
    role_data: ChangeRoleRequest,
    id: int = Path(..., description="ID пользователя"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Добавление роли пользователю (только для администраторов)
    
    Args:
        role_data: Данные роли для добавления
        id: ID пользователя
        current_user: Текущий пользователь с ролью admin
        db: Сессия базы данных
    
    Returns:
        Dict[str, Any]: Результат операции
    
    Raises:
        HTTPException: При ошибке добавления роли
    """
    try:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        
        # Проверяем существование пользователя
        user = await user_repo.get_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {id} не найден"
            )
        
        # Проверяем существование роли
        role = await role_repo.get_by_id(role_data.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Роль с ID {role_data.role_id} не найдена"
            )
        
        # Проверяем, есть ли уже у пользователя эта роль
        if any(r.id == role.id for r in user.roles):
            return {
                "user_id": user.id,
                "role": {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description
                },
                "message": f"Роль '{role.name}' уже присвоена пользователю"
            }
        
        # Добавляем роль пользователю
        await user_repo.add_role(user.id, role.id)
        
        return {
            "user_id": user.id,
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description
            },
            "message": f"Роль '{role.name}' успешно добавлена пользователю"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при добавлении роли пользователю: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при добавлении роли пользователю"
        )

@router.delete("/{id}/roles/{role_id}", response_model=RemoveRoleResponse)
@check_role("admin")
async def remove_role_from_user(
    id: int = Path(..., description="ID пользователя"),
    role_id: int = Path(..., description="ID роли"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Удаление роли у пользователя (только для администраторов)
    
    Args:
        id: ID пользователя
        role_id: ID роли
        current_user: Текущий пользователь с ролью admin
        db: Сессия базы данных
    
    Returns:
        Dict[str, Any]: Результат операции
    
    Raises:
        HTTPException: При ошибке удаления роли
    """
    try:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        
        # Проверяем существование пользователя
        user = await user_repo.get_by_id(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {id} не найден"
            )
        
        # Проверяем существование роли
        role = await role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Роль с ID {role_id} не найдена"
            )
        
        # Проверяем, есть ли у пользователя эта роль
        if not any(r.id == role.id for r in user.roles):
            return {
                "user_id": user.id,
                "role_id": role.id,
                "message": f"Роль '{role.name}' не присвоена пользователю"
            }
        
        # Проверяем, это последняя роль или нет
        if len(user.roles) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить последнюю роль пользователя"
            )
        
        # Удаляем роль у пользователя
        await user_repo.remove_role(user.id, role.id)
        
        return {
            "user_id": user.id,
            "role_id": role.id,
            "message": f"Роль '{role.name}' успешно удалена у пользователя"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при удалении роли у пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении роли у пользователя"
        ) 