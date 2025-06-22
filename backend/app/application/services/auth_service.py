import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import jwt
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domain.models.role import Role
from app.domain.models.user import User
from app.infrastructure.cache.redis_service import RedisService
from app.infrastructure.database import get_db
from app.infrastructure.database.repositories import RoleRepository, UserRepository, OAuthRepository

from .base import (AuthenticationError, BaseService, ValidationError)

# Инициализация контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройки JWT - берем непосредственно из settings
# ALGORITHM = settings.ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
# REFRESH_TOKEN_EXPIRE_DAYS = 30  # Refresh токены длиннее, чем access

logger = logging.getLogger(__name__)

class AuthService(BaseService):
    """Сервис для аутентификации и авторизации пользователей"""
    
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        redis_cache: Any = None
    ):
        super().__init__()
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.redis_cache = redis_cache or RedisService()
        
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить соответствие пароля хешу"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _get_password_hash(self, password: str) -> str:
        """Получить хеш пароля"""
        return pwd_context.hash(password)
    
    def _create_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Создать JWT токен
        
        Args:
            data: Данные для добавления в токен
            expires_delta: Время жизни токена
            
        Returns:
            str: Строка JWT токена
        """
        to_encode = data.copy()
        
        # Устанавливаем время истечения токена
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)  # По умолчанию 15 минут
            
        to_encode.update({"exp": expire})
        
        # Создаем JWT токен
        try:
            # Пробуем использовать PyJWT
            try:
                import jwt
                encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
                # В зависимости от версии PyJWT, encode возвращает bytes или str
                if isinstance(encoded_jwt, bytes):
                    encoded_jwt = encoded_jwt.decode('utf-8')
                return encoded_jwt
            except (ImportError, AttributeError):
                # Если PyJWT не установлен или не содержит нужного метода, пробуем python-jose
                from jose import jwt
                encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
                return encoded_jwt
        except Exception as e:
            self._log_error(f"Ошибка при создании JWT токена", e)
            raise
    
    def _decode_token(self, token: str) -> Dict[str, Any]:
        """
        Декодировать JWT токен
        
        Args:
            token: JWT токен для декодирования
            
        Returns:
            Dict[str, Any]: Декодированные данные из токена
            
        Raises:
            AuthenticationError: Если токен просрочен или недействителен
        """
        try:
            # Пробуем использовать PyJWT
            try:
                import jwt
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    return payload
                except jwt.ExpiredSignatureError:
                    self._log_info(f"Попытка использования просроченного токена")
                    raise AuthenticationError("Срок действия токена истек")
                except jwt.InvalidTokenError as e:
                    self._log_error(f"Ошибка при декодировании токена", e)
                    raise AuthenticationError("Недействительный токен")
            except (ImportError, AttributeError):
                # Если PyJWT не установлен или не содержит нужного метода, пробуем python-jose
                from jose import ExpiredSignatureError, JWTError, jwt
                try:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    return payload
                except ExpiredSignatureError:
                    self._log_info(f"Попытка использования просроченного токена")
                    raise AuthenticationError("Срок действия токена истек")
                except JWTError as e:
                    self._log_error(f"Ошибка при декодировании токена", e)
                    raise AuthenticationError("Недействительный токен")
        except (ImportError, AttributeError) as e:
            self._log_error(f"Ошибка при импорте JWT библиотеки", e)
            raise AuthenticationError("Ошибка при обработке токена")
    
    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Аутентифицировать пользователя по email и паролю
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            
        Returns:
            User: Аутентифицированный пользователь
            
        Raises:
            AuthenticationError: При неверных учетных данных или неактивном пользователе
        """
        try:
            # Получаем пользователя с предзагрузкой ролей
            user = await self.user_repository.get_by_email_with_roles(email)
            
            if not user:
                self._log_info(f"Неудачная попытка входа с несуществующим email: {email}")
                raise AuthenticationError("Неверные учетные данные")
            
            if not user.is_active:
                self._log_info(f"Попытка входа заблокированного пользователя: {email}")
                raise AuthenticationError("Пользователь заблокирован")
            
            if not user.hashed_password:
                self._log_info(f"Попытка входа по паролю для OAuth аккаунта: {email}")
                raise AuthenticationError("Для этого аккаунта требуется OAuth аутентификация")
            
            if not self._verify_password(password, user.hashed_password):
                self._log_info(f"Неудачная попытка входа с неверным паролем для {email}")
                raise AuthenticationError("Неверные учетные данные")
            
            self._log_info(f"Успешная аутентификация пользователя: {email}")
            return user
        except AuthenticationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при аутентификации пользователя", e)
            raise AuthenticationError("Ошибка при аутентификации")
    
    async def create_tokens(self, user: User) -> Dict[str, str]:
        """
        Создать пару токенов: access и refresh
        
        Args:
            user: Пользователь, для которого создаются токены
            
        Returns:
            Dict[str, str]: Словарь с токенами и метаданными
        """
        try:
            # Получаем роли пользователя
            # Если роли уже загружены (через User.roles), используем их
            # Если нет, получаем их через явный запрос
            user_roles = []
            if user.roles:
                # Роли уже загружены
                user_roles = [role.name for role in user.roles]
            else:
                # Роли не загружены, получаем их отдельным запросом
                roles = await self.role_repository.get_roles_for_user(user.id)
                user_roles = [role.name for role in roles]
            
            # Создаем данные для payload токена
            access_token_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": user_roles,
                "type": "access"
            }
            
            # Создаем уникальный jti (JWT ID) для refresh токена
            jti = str(uuid.uuid4())
            
            refresh_token_data = {
                "sub": str(user.id),
                "jti": jti,
                "type": "refresh"
            }
            
            # Устанавливаем время жизни токенов
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
            # Создаем токены
            access_token = self._create_token(access_token_data, access_token_expires)
            refresh_token = self._create_token(refresh_token_data, refresh_token_expires)
            
            self._log_info(f"Созданы токены для пользователя ID: {user.id}")
            
            # Возвращаем пару токенов и время жизни access токена
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # в секундах
            }
        except Exception as e:
            self._log_error(f"Ошибка при создании токенов для пользователя ID: {user.id}", e)
            raise
    
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
        """
        Обновить токены с использованием refresh токена
        
        Args:
            refresh_token: Refresh токен для обновления
            
        Returns:
            Dict[str, str]: Новая пара токенов и метаданные
            
        Raises:
            AuthenticationError: При неверном токене или неактивном пользователе
        """
        try:
            # Проверяем refresh токен на наличие в черном списке
            is_blacklisted = await self.redis_cache.is_token_blacklisted(refresh_token)
            if is_blacklisted:
                self._log_info(f"Попытка использования токена из черного списка")
                raise AuthenticationError("Токен в черном списке")
            
            # Декодируем токен
            payload = self._decode_token(refresh_token)
            
            # Проверяем, что это refresh токен
            if payload.get("type") != "refresh":
                self._log_info(f"Попытка использования не-refresh токена для обновления")
                raise AuthenticationError("Невалидный refresh токен")
                
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            if not user_id or not jti:
                self._log_info(f"Попытка использования неверного формата токена без sub или jti")
                raise AuthenticationError("Неверный формат токена")
                
            # Получаем пользователя
            user = await self.user_repository.get_by_id(int(user_id))
            
            # Проверяем активность пользователя
            if not user.is_active:
                self._log_info(f"Попытка обновления токенов для заблокированного пользователя ID: {user_id}")
                raise AuthenticationError("Пользователь заблокирован")
            
            # Добавляем старый токен в черный список
            # Используем время жизни из payload токена
            exp_time = payload.get("exp", 0)
            current_time = int(datetime.utcnow().timestamp())
            ttl = max(0, exp_time - current_time)  # Остаточное время жизни в секундах
            
            await self.redis_cache.add_token_to_blacklist(refresh_token, ttl)
            
            self._log_info(f"Обновлены токены для пользователя ID: {user_id}")
            
            # Создаем новые токены
            return await self.create_tokens(user)
            
        except AuthenticationError:
            raise
        except (jwt.PyJWTError, ValueError) as e:
            self._log_error(f"Ошибка при обработке refresh токена", e)
            raise AuthenticationError("Неверный формат токена")
        except Exception as e:
            self._log_error(f"Неожиданная ошибка при обновлении токенов", e)
            raise AuthenticationError("Ошибка при обновлении токенов")
    
    async def logout(self, refresh_token: str) -> bool:
        """
        Выход пользователя, инвалидация refresh токена
        
        Args:
            refresh_token: Refresh токен для инвалидации
            
        Returns:
            bool: Успешность операции
        """
        try:
            # Декодируем токен
            payload = self._decode_token(refresh_token)
            
            # Получаем время истечения токена
            exp_time = payload.get("exp", 0)
            current_time = int(datetime.utcnow().timestamp())
            ttl = max(0, exp_time - current_time)  # Остаточное время жизни в секундах
            
            # Добавляем токен в черный список
            result = await self.redis_cache.add_token_to_blacklist(refresh_token, ttl)
            
            user_id = payload.get("sub")
            if user_id:
                self._log_info(f"Пользователь ID: {user_id} вышел из системы")
            
            return result
        except Exception as e:
            self._log_error(f"Ошибка при выходе пользователя", e)
            return False
    
    async def get_current_user(self, token: str) -> User:
        """
        Получить текущего пользователя по JWT токену
        
        Args:
            token: JWT токен для проверки
            
        Returns:
            User: Пользователь из токена
            
        Raises:
            AuthenticationError: При неверном токене или неактивном пользователе
        """
        try:
            # Проверяем, что токен не в черном списке
            is_blacklisted = await self.redis_cache.is_token_blacklisted(token)
            if is_blacklisted:
                self._log_info(f"Попытка использования токена из черного списка")
                raise AuthenticationError("Токен в черном списке")
            
            # Декодируем токен
            payload = self._decode_token(token)
            
            # Проверяем, что это access токен
            if payload.get("type") != "access":
                self._log_info(f"Попытка использования не-access токена для авторизации")
                raise AuthenticationError("Требуется access токен")
            
            user_id = payload.get("sub")
            if user_id is None:
                self._log_info(f"Токен без идентификатора пользователя (sub)")
                raise AuthenticationError("Неверный формат токена")
            
            # Получаем пользователя с ролями
            try:
                user = await self.user_repository.get_by_id_with_roles(int(user_id))
            except Exception as e:
                self._log_error(f"Ошибка при получении пользователя ID: {user_id} из базы данных", e)
                raise AuthenticationError("Пользователь не найден")
            
            if not user.is_active:
                self._log_info(f"Попытка авторизации заблокированного пользователя ID: {user_id}")
                raise AuthenticationError("Пользователь заблокирован")
            
            return user
        except AuthenticationError:
            raise
        except Exception as e:
            self._log_error(f"Неожиданная ошибка при получении текущего пользователя", e)
            raise AuthenticationError("Ошибка авторизации")
    
    async def check_permission(self, user: User, permission: str) -> bool:
        """
        Проверить наличие разрешения у пользователя
        
        Args:
            user: Пользователь для проверки
            permission: Строка разрешения
            
        Returns:
            bool: True если у пользователя есть разрешение
        """
        try:
            if not user:
                return False
                
            # Получаем ID ролей пользователя
            role_ids = [role.id for role in user.roles]
            
            # Проверяем наличие разрешения
            has_permission = await self.permission_repository.check_permission(role_ids, permission)
            
            if not has_permission:
                self._log_debug(f"Пользователь ID: {user.id} не имеет разрешения: {permission}")
                
            return has_permission
        except Exception as e:
            self._log_error(f"Ошибка при проверке разрешения '{permission}' для пользователя ID: {user.id}", e)
            return False
    
    async def register_user(self, user_data: Dict[str, Any]) -> User:
        """
        Регистрация нового пользователя
        
        Args:
            user_data: Данные нового пользователя
            
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValidationError: При ошибках валидации данных
        """
        try:
            # Валидация email
            if not user_data.get("email"):
                raise ValidationError("Email обязателен")
                
            # Проверка формата email (тут можно использовать regex или библиотеку для более точной проверки)
            if "@" not in user_data.get("email", ""):
                raise ValidationError("Некорректный формат email")
            
            # Проверяем, не занят ли email
            existing_user = await self.user_repository.get_by_email(user_data["email"])
            if existing_user:
                raise ValidationError(f"Пользователь с email {user_data['email']} уже существует")
            
            # Проверяем, не занят ли username
            if "username" in user_data:
                if not user_data["username"] or len(user_data["username"]) < 3:
                    raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
                    
                existing_username = await self.user_repository.get_by_username(user_data["username"])
                if existing_username:
                    raise ValidationError(f"Пользователь с именем {user_data['username']} уже существует")
            
            # Валидация пароля
            if "password" in user_data:
                if not user_data["password"] or len(user_data["password"]) < 8:
                    raise ValidationError("Пароль должен содержать минимум 8 символов")
                
                # Хешируем пароль
                hashed_password = self._get_password_hash(user_data["password"])
                user_data["hashed_password"] = hashed_password
                del user_data["password"]  # Удаляем открытый пароль
            
            # Генерируем токен для верификации email
            import uuid
            from datetime import datetime, timedelta
            verification_token = str(uuid.uuid4())
            verification_expires = datetime.utcnow() + timedelta(days=1)  # 24 часа на верификацию
            
            user_data["verification_token"] = verification_token
            user_data["verification_token_expires_at"] = verification_expires
            user_data["is_verified"] = False
            
            # Получаем роль "user", если она существует
            default_role = await self.role_repository.get_by_name("user")
            
            # Создаем пользователя (без роли сначала)
            create_data = user_data.copy()
            if "role" in create_data:
                del create_data["role"]  # Удаляем поле role, так как оно не соответствует модели User
            
            user = await self.user_repository.create(create_data)
            
            # Назначаем роль "user", если она существует
            if default_role:
                await self.user_repository.add_role_to_user(user.id, default_role.id)
            
            self._log_info(f"Зарегистрирован новый пользователь: {user.email} (ID: {user.id})")
            
            return user
        except Exception as e:
            self._log_error(f"Ошибка при регистрации пользователя: {str(e)}", e)
            raise ValidationError("Ошибка при регистрации пользователя")
        
    async def verify_email(self, verification_token: str) -> bool:
        """
        Верификация email пользователя
        
        Args:
            verification_token: Токен верификации
            
        Returns:
            bool: Успешность верификации
        """
        try:
            user = await self.user_repository.verify_user(verification_token)
            if user:
                self._log_info(f"Подтвержден email пользователя ID: {user.id}")
                return True
            else:
                self._log_info(f"Неудачная попытка верификации с токеном: {verification_token}")
                return False
        except Exception as e:
            self._log_error(f"Ошибка при верификации email", e)
            return False
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """
        Запрос на сброс пароля
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[str]: Токен для сброса пароля или None
        """
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                # Не сообщаем, что пользователь не существует, чтобы избежать утечки информации
                self._log_info(f"Запрос сброса пароля для несуществующего email: {email}")
                return None
                
            # Генерируем токен для сброса пароля
            reset_token = str(uuid.uuid4())
            reset_token_expires = datetime.utcnow() + timedelta(hours=1)  # 1 час на сброс
            
            # Устанавливаем токен для пользователя
            await self.user_repository.set_reset_token(user.id, reset_token, reset_token_expires)
            
            self._log_info(f"Создан токен сброса пароля для пользователя ID: {user.id}")
            
            return reset_token
        except Exception as e:
            self._log_error(f"Ошибка при создании запроса на сброс пароля для {email}", e)
            return None
    
    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Сброс пароля по токену
        
        Args:
            reset_token: Токен сброса пароля
            new_password: Новый пароль
            
        Returns:
            bool: Успешность сброса пароля
        """
        try:
            # Валидация пароля
            if not new_password or len(new_password) < 8:
                self._log_info(f"Попытка сброса пароля с недостаточно надежным паролем")
                return False
            
            # Ищем пользователя по токену сброса
            user = await self.user_repository.find_by_reset_token(reset_token)
            
            if not user:
                self._log_info(f"Попытка сброса пароля с неверным токеном: {reset_token}")
                return False
                
            # Проверяем, не истек ли токен
            if user.reset_token_expires_at and user.reset_token_expires_at < datetime.utcnow():
                # Очищаем истекший токен
                await self.user_repository.clear_reset_token(user.id)
                self._log_info(f"Попытка сброса пароля с истекшим токеном для пользователя ID: {user.id}")
                return False
                
            # Хешируем новый пароль
            hashed_password = self._get_password_hash(new_password)
            
            # Обновляем пароль и очищаем токен сброса
            await self.user_repository.update(user.id, {
                "hashed_password": hashed_password,
                "reset_token": None,
                "reset_token_expires_at": None
            })
            
            self._log_info(f"Успешный сброс пароля для пользователя ID: {user.id}")
            
            return True
        except Exception as e:
            self._log_error(f"Ошибка при сбросе пароля", e)
            return False
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Изменение пароля пользователя
        
        Args:
            user_id: ID пользователя
            current_password: Текущий пароль
            new_password: Новый пароль
            
        Returns:
            bool: Успешность изменения пароля
            
        Raises:
            ValidationError: При ошибках валидации пароля
        """
        try:
            # Валидация нового пароля
            if not new_password or len(new_password) < 8:
                raise ValidationError("Новый пароль должен содержать минимум 8 символов")
            
            user = await self.user_repository.get_by_id(user_id)
            
            # Проверяем текущий пароль
            if not self._verify_password(current_password, user.hashed_password):
                self._log_info(f"Попытка смены пароля с неверным текущим паролем для пользователя ID: {user_id}")
                raise ValidationError("Неверный текущий пароль")
                
            # Хешируем новый пароль
            hashed_password = self._get_password_hash(new_password)
            
            # Обновляем пароль
            await self.user_repository.update(user_id, {"hashed_password": hashed_password})
            
            self._log_info(f"Успешная смена пароля для пользователя ID: {user_id}")
            
            return True
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при смене пароля для пользователя ID: {user_id}", e)
            raise ValidationError("Ошибка при смене пароля")
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Получить все разрешения пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[str]: Список строк разрешений
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            
            # Получаем ID ролей пользователя
            role_ids = [role.id for role in user.roles]
            
            # Получаем все разрешения для этих ролей
            permissions = await self.permission_repository.get_by_roles(role_ids)
            
            return [permission.name for permission in permissions]
        except Exception as e:
            self._log_error(f"Ошибка при получении разрешений пользователя ID: {user_id}", e)
            return []
    
    async def oauth_associate_user(self, provider: str, provider_user_id: str, user_data: Dict[str, Any]) -> User:
        """
        Связать OAuth аккаунт с существующим пользователем или создать нового
        
        Args:
            provider: Название OAuth провайдера (google, vk, yandex)
            provider_user_id: ID пользователя у провайдера
            user_data: Данные пользователя от провайдера
            
        Returns:
            User: Существующий или новый пользователь
        """
        try:
            
            oauth_repository = OAuthRepository(self.db)
            
            # Валидация данных от OAuth
            if not provider or not provider_user_id:
                self._log_error(f"Отсутствуют обязательные данные для OAuth: provider={provider}, provider_user_id={provider_user_id}")
                raise ValidationError("Отсутствуют обязательные данные от OAuth провайдера")
            
            # Проверяем, существует ли уже такой OAuth аккаунт
            oauth_account = await oauth_repository.get_by_provider_and_id(provider, provider_user_id)
            
            if oauth_account:
                # Если OAuth аккаунт существует, получаем пользователя
                user = await self.user_repository.get_by_id(oauth_account.user_id)
                self._log_info(f"OAuth вход существующего пользователя ID: {user.id} через {provider}")
                return user
                
            # Проверяем, существует ли пользователь с таким email
            email = user_data.get("email")
            if email:
                existing_user = await self.user_repository.get_by_email(email)
                
                if existing_user:
                    # Связываем существующего пользователя с OAuth аккаунтом
                    oauth_data = {
                        "user_id": existing_user.id,
                        "provider": provider,
                        "provider_user_id": provider_user_id,
                        "access_token": user_data.get("access_token"),
                        "refresh_token": user_data.get("refresh_token"),
                        "expires_at": user_data.get("expires_at"),
                        "token_type": user_data.get("token_type"),
                        "scopes": user_data.get("scopes")
                    }
                    
                    await oauth_repository.create(oauth_data)
                    self._log_info(f"Связан OAuth аккаунт {provider} с существующим пользователем ID: {existing_user.id}")
                    return existing_user
            
            # Создаем нового пользователя и связываем его с OAuth аккаунтом
            # Преобразуем данные из OAuth в формат пользователя
            username = user_data.get("username") or f"{provider}_{provider_user_id}"
            
            # Проверяем уникальность username
            existing_username = await self.user_repository.get_by_username(username)
            if existing_username:
                # Если имя пользователя занято, добавляем случайный суффикс
                username = f"{username}_{uuid.uuid4().hex[:6]}"
            
            new_user_data = {
                "email": email,
                "username": username,
                "first_name": user_data.get("first_name") or "",
                "last_name": user_data.get("last_name") or "",
                "avatar_url": user_data.get("avatar_url"),
                "is_verified": True  # Пользователи через OAuth считаются верифицированными
            }
            
            # Создаем пользователя
            user = await self.user_repository.create(new_user_data)
            
            # Получаем роль "user", если она существует
            default_role = await self.role_repository.get_by_name("user")
            
            # Назначаем роль "user", если она существует
            if default_role:
                await self.user_repository.add_role_to_user(user.id, default_role.id)
            
            # Создаем OAuth запись
            oauth_data = {
                "user_id": user.id,
                "provider": provider,
                "provider_user_id": provider_user_id,
                "access_token": user_data.get("access_token"),
                "refresh_token": user_data.get("refresh_token"),
                "expires_at": user_data.get("expires_at"),
                "token_type": user_data.get("token_type"),
                "scopes": user_data.get("scopes")
            }
            
            await oauth_repository.create(oauth_data)
            self._log_info(f"Создан новый пользователь ID: {user.id} через OAuth {provider}")
            
            return user
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обработке OAuth авторизации через {provider}", e)
            raise ValidationError("Ошибка при обработке OAuth авторизации") 