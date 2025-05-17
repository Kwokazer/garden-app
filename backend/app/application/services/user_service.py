import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.database.repositories import (RoleRepository,
                                                      UserRepository)

from .base import (AuthorizationError, BaseService, NotFoundError,
                   ValidationError)

logger = logging.getLogger(__name__)

class UserService(BaseService):
    """Сервис для работы с пользователями"""
    
    def __init__(
        self,
        db: AsyncSession,
        redis_cache: Optional[RedisCache] = None
    ):
        super().__init__()
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.redis_cache = redis_cache or RedisCache()

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            User: Пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            return user
        except Exception as e:
            self._log_error(f"Ошибка при получении пользователя по ID {user_id}", e)
            raise
    
    async def get_user_by_email(self, email: str) -> User:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            User: Пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise NotFoundError(f"Пользователь с email {email} не найден")
            return user
        except Exception as e:
            self._log_error(f"Ошибка при получении пользователя по email {email}", e)
            raise
    
    async def get_user_by_username(self, username: str) -> User:
        """
        Получить пользователя по имени пользователя
        
        Args:
            username: Имя пользователя
            
        Returns:
            User: Пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        try:
            user = await self.user_repository.get_by_username(username)
            if not user:
                raise NotFoundError(f"Пользователь с именем {username} не найден")
            return user
        except Exception as e:
            self._log_error(f"Ошибка при получении пользователя по имени {username}", e)
            raise
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """
        Обновить данные пользователя
        
        Args:
            user_id: ID пользователя
            user_data: Данные для обновления
            
        Returns:
            User: Обновленный пользователь
            
        Raises:
            NotFoundError: Если пользователь не найден
            ValidationError: Если данные не валидны
        """
        try:
            # Проверяем, существует ли пользователь
            existing_user = await self.user_repository.get_by_id(user_id)
            if not existing_user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            # Проверка уникальности email, если он изменяется
            if "email" in user_data and user_data["email"] != existing_user.email:
                email_user = await self.user_repository.get_by_email(user_data["email"])
                if email_user:
                    raise ValidationError(f"Email {user_data['email']} уже используется")
            
            # Проверка уникальности username, если он изменяется
            if "username" in user_data and user_data["username"] != existing_user.username:
                username_user = await self.user_repository.get_by_username(user_data["username"])
                if username_user:
                    raise ValidationError(f"Имя пользователя {user_data['username']} уже используется")
            
            # Обновляем пользователя
            updated_user = await self.user_repository.update(user_id, user_data)
            self._log_info(f"Обновлен пользователь ID: {user_id}")
            
            return updated_user
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении пользователя ID: {user_id}", e)
            raise ValidationError("Ошибка при обновлении пользователя")
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: Успешность удаления
            
        Raises:
            NotFoundError: Если пользователь не найден
        """
        try:
            # Проверяем, существует ли пользователь
            existing_user = await self.user_repository.get_by_id(user_id)
            if not existing_user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            # Удаляем пользователя
            result = await self.user_repository.delete(user_id)
            self._log_info(f"Удален пользователь ID: {user_id}")
            
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении пользователя ID: {user_id}", e)
            raise ValidationError("Ошибка при удалении пользователя")
    
    async def add_role_to_user(self, user_id: int, role_name: str) -> User:
        """
        Добавить роль пользователю
        
        Args:
            user_id: ID пользователя
            role_name: Название роли
            
        Returns:
            User: Обновленный пользователь
            
        Raises:
            NotFoundError: Если пользователь или роль не найдены
        """
        try:
            # Проверяем, существует ли пользователь
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            # Проверяем, существует ли роль
            role = await self.role_repository.get_by_name(role_name)
            if not role:
                raise NotFoundError(f"Роль {role_name} не найдена")
            
            # Проверяем, есть ли уже такая роль у пользователя
            has_role = any(r.name == role_name for r in user.roles)
            if has_role:
                return user  # Роль уже назначена
            
            # Добавляем роль пользователю
            await self.user_repository.add_role_to_user(user_id, role.id)
            
            # Получаем обновленного пользователя
            updated_user = await self.user_repository.get_by_id(user_id)
            self._log_info(f"Добавлена роль {role_name} пользователю ID: {user_id}")
            
            return updated_user
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при добавлении роли {role_name} пользователю ID: {user_id}", e)
            raise ValidationError(f"Ошибка при добавлении роли {role_name}")
    
    async def remove_role_from_user(self, user_id: int, role_name: str) -> User:
        """
        Удалить роль у пользователя
        
        Args:
            user_id: ID пользователя
            role_name: Название роли
            
        Returns:
            User: Обновленный пользователь
            
        Raises:
            NotFoundError: Если пользователь или роль не найдены
        """
        try:
            # Проверяем, существует ли пользователь
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"Пользователь с ID {user_id} не найден")
            
            # Проверяем, существует ли роль
            role = await self.role_repository.get_by_name(role_name)
            if not role:
                raise NotFoundError(f"Роль {role_name} не найдена")
            
            # Проверяем, есть ли роль у пользователя
            has_role = any(r.name == role_name for r in user.roles)
            if not has_role:
                return user  # У пользователя нет такой роли
            
            # Удаляем роль у пользователя
            await self.user_repository.remove_role_from_user(user_id, role.id)
            
            # Получаем обновленного пользователя
            updated_user = await self.user_repository.get_by_id(user_id)
            self._log_info(f"Удалена роль {role_name} у пользователя ID: {user_id}")
            
            return updated_user
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении роли {role_name} у пользователя ID: {user_id}", e)
            raise ValidationError(f"Ошибка при удалении роли {role_name}")
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Получить список всех пользователей с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            
        Returns:
            List[User]: Список пользователей
        """
        try:
            users = await self.user_repository.get_all(skip=skip, limit=limit)
            return users
        except Exception as e:
            self._log_error(f"Ошибка при получении списка пользователей", e)
            return [] 