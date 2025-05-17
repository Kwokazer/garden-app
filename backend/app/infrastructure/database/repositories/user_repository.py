import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select, text, update, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.role import Role
from app.domain.models.user import User, UserRole, user_role

from .base import BaseRepository, DatabaseError, EntityNotFoundError

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return await self.get_by_field("email", email)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени пользователя"""
        return await self.get_by_field("username", username)
    
    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Поиск пользователей по имени, фамилии или имени пользователя"""
        try:
            search_query = f"%{query}%"
            statement = (
                select(User)
                .where(
                    or_(
                        User.username.ilike(search_query),
                        User.first_name.ilike(search_query),
                        User.last_name.ilike(search_query),
                        User.email.ilike(search_query)
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            
            result = await self.session.execute(statement)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске пользователей: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def add_role_to_user(self, user_id: int, role_id: int) -> User:
        """Добавить роль пользователю"""
        try:
            # Проверяем существование пользователя
            user = await self.get_by_id(user_id)
            
            # Проверяем существование роли
            role_query = select(Role).filter(Role.id == role_id)
            role_result = await self.session.execute(role_query)
            role = role_result.scalars().first()
            
            if not role:
                raise EntityNotFoundError("Role", role_id)
            
            # Проверяем существует ли связь
            query = select(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            )
            result = await self.session.execute(query)
            
            # Если связи нет, создаем ее
            if not result.scalars().first():
                new_relation = UserRole(
                    user_id=user_id,
                    role_id=role_id
                )
                self.session.add(new_relation)
                await self.session.commit()
            
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при добавлении роли пользователю: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def remove_role_from_user(self, user_id: int, role_id: int) -> User:
        """Удалить роль у пользователя"""
        try:
            # Проверяем существование пользователя
            user = await self.get_by_id(user_id)
            
            # Находим существующую связь
            query = select(UserRole).filter(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.role_id == role_id
                )
            )
            result = await self.session.execute(query)
            relation = result.scalars().first()
            
            # Если связь существует, удаляем ее
            if relation:
                await self.session.delete(relation)
                await self.session.commit()
            
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении роли у пользователя: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def count_active_users(self) -> int:
        """Получить количество активных пользователей"""
        try:
            query = select(func.count(User.id)).where(User.is_active == True)
            result = await self.session.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчёте активных пользователей: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def verify_user(self, verification_token: str) -> Optional[User]:
        """Верифицировать пользователя по токену верификации"""
        try:
            # Ищем пользователя по токену верификации
            query = select(User).where(User.verification_token == verification_token)
            result = await self.session.execute(query)
            user = result.scalars().first()
            
            if not user:
                return None
            
            # Обновляем статус верификации
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires_at = None
            
            await self.session.flush()
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при верификации пользователя: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
            
    async def set_reset_token(self, user_id: int, reset_token: str, expires_at: Any) -> User:
        """Установить токен для сброса пароля"""
        try:
            user = await self.get_by_id(user_id)
            user.reset_token = reset_token
            user.reset_token_expires_at = expires_at
            await self.session.flush()
            return user
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при установке токена сброса пароля: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def find_by_reset_token(self, reset_token: str) -> Optional[User]:
        """Найти пользователя по токену сброса пароля"""
        try:
            query = select(User).where(User.reset_token == reset_token)
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске пользователя по токену сброса: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def clear_reset_token(self, user_id: int) -> User:
        """Очистить токен сброса пароля после использования"""
        try:
            user = await self.get_by_id(user_id)
            user.reset_token = None
            user.reset_token_expires_at = None
            await self.session.flush()
            return user
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при очистке токена сброса пароля: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
            
    async def get_users_with_role(self, role_name: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить всех пользователей с определенной ролью"""
        try:
            query = (
                select(User)
                .join(User.roles)
                .where(Role.name == role_name)
                .offset(skip)
                .limit(limit)
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователей с ролью {role_name}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
            
    async def check_unique_fields(self, email: Optional[str] = None, username: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, str]:
        """
        Проверяет уникальность email и username.
        
        Args:
            email: Email для проверки
            username: Имя пользователя для проверки
            user_id: ID пользователя, которого нужно исключить из проверки (при обновлении)
            
        Returns:
            Dict[str, str]: Словарь с ошибками в формате {поле: сообщение об ошибке}
            Пустой словарь означает отсутствие ошибок
        """
        errors = {}
        
        if email:
            existing_user = await self.get_by_email(email)
            if existing_user and (user_id is None or existing_user.id != user_id):
                errors["email"] = f"Пользователь с email {email} уже существует"
        
        if username:
            existing_user = await self.get_by_username(username)
            if existing_user and (user_id is None or existing_user.id != user_id):
                errors["username"] = f"Пользователь с именем {username} уже существует"
        
        return errors 
    
    async def get_by_email_with_roles(self, email: str) -> Optional[User]:
        """Получить пользователя по email с загрузкой ролей"""
        try:
            stmt = (
                select(User)
                .options(selectinload(User.roles))  # Предзагружаем роли
                .where(User.email == email)
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении пользователя по email с ролями: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}") 