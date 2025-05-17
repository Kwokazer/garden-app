import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.permission import Permission
from app.domain.models.role import Role, role_permission, RolePermission

from .base import BaseRepository, DatabaseError, EntityNotFoundError

logger = logging.getLogger(__name__)

class RoleRepository(BaseRepository[Role]):
    """Репозиторий для работы с ролями"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Role)
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Получить роль по имени"""
        return await self.get_by_field("name", name)
    
    async def get_with_permissions(self, role_id: int) -> Optional[Role]:
        """Получить роль с загруженными разрешениями"""
        try:
            query = (
                select(Role)
                .where(Role.id == role_id)
                .options(selectinload(Role.permissions))
            )
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении роли с разрешениями: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def add_permission(self, role_id: int, permission_id: int) -> Role:
        """Добавить разрешение к роли"""
        try:
            # Получаем роль
            role = await self.get_by_id(role_id)
            
            # Получаем разрешение
            permission_query = select(Permission).where(Permission.id == permission_id)
            permission_result = await self.session.execute(permission_query)
            permission = permission_result.scalars().first()
            
            if not permission:
                raise EntityNotFoundError("Permission", permission_id)
            
            # Проверяем существует ли связь
            query = select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            result = await self.session.execute(query)
            
            # Если связи нет, создаем ее
            if not result.scalars().first():
                new_relation = RolePermission(
                    role_id=role_id,
                    permission_id=permission_id
                )
                self.session.add(new_relation)
                await self.session.commit()
            
            return role
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при добавлении разрешения к роли: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def remove_permission(self, role_id: int, permission_id: int) -> Role:
        """Удалить разрешение из роли"""
        try:
            # Получаем роль
            role = await self.get_by_id(role_id)
            
            # Находим существующую связь
            query = select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            result = await self.session.execute(query)
            relation = result.scalars().first()
            
            # Если связь существует, удаляем ее
            if relation:
                await self.session.delete(relation)
                await self.session.commit()
            
            return role
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении разрешения из роли: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_roles_for_user(self, user_id: int) -> List[Role]:
        """Получить роли для указанного пользователя"""
        try:
            query = (
                select(Role)
                .join(Role.users)
                .where(Role.users.any(id=user_id))
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении ролей пользователя ID {user_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")

class PermissionRepository(BaseRepository[Permission]):
    """Репозиторий для работы с разрешениями"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Permission)
    
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Получить разрешение по имени"""
        return await self.get_by_field("name", name)
    
    async def get_by_roles(self, role_ids: List[int]) -> List[Permission]:
        """Получить все разрешения, связанные с указанными ролями"""
        try:
            if not role_ids:
                return []
                
            query = (
                select(Permission)
                .join(Permission.roles)
                .where(Role.id.in_(role_ids))
                .distinct()
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении разрешений по ролям: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def check_permission(self, role_ids: List[int], permission_name: str) -> bool:
        """Проверить, имеется ли указанное разрешение хотя бы в одной из ролей"""
        try:
            if not role_ids:
                return False
                
            query = (
                select(func.count())
                .select_from(Permission)
                .join(Permission.roles)
                .where(
                    and_(
                        Role.id.in_(role_ids),
                        Permission.name == permission_name
                    )
                )
            )
            result = await self.session.execute(query)
            count = result.scalar()
            return count > 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке разрешения: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}") 