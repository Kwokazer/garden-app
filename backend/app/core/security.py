import datetime
from typing import Any, Dict, Optional, Union

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Класс для работы с JWT токенами
class JWTHandler:
    @staticmethod
    def create_access_token(
        subject: Union[str, int],
        expires_delta: Optional[datetime.timedelta] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Создает JWT токен доступа
        
        Args:
            subject: ID пользователя или другой идентификатор
            expires_delta: Время жизни токена
            payload: Дополнительные данные для включения в токен
            
        Returns:
            str: JWT токен
        """
        if expires_delta is None:
            expires_delta = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        # Определяем время истечения токена
        expire = datetime.datetime.utcnow() + expires_delta
        
        # Формируем базовый payload
        token_payload = {
            "exp": expire,
            "sub": str(subject),
            "type": "access"
        }
        
        # Добавляем дополнительные данные, если они есть
        if payload:
            token_payload.update(payload)
            
        # Создаем закодированный токен
        encoded_jwt = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        subject: Union[str, int],
        expires_delta: Optional[datetime.timedelta] = None
    ) -> str:
        """
        Создает JWT токен обновления
        
        Args:
            subject: ID пользователя или другой идентификатор
            expires_delta: Время жизни токена
            
        Returns:
            str: JWT токен обновления
        """
        if expires_delta is None:
            expires_delta = datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
        expire = datetime.datetime.utcnow() + expires_delta
        
        # Формируем payload для токена обновления
        token_payload = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh"
        }
        
        # Создаем закодированный токен
        encoded_jwt = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Декодирует JWT токен
        
        Args:
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Данные из токена
            
        Raises:
            jwt.PyJWTError: Если токен недействителен
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"Ошибка при декодировании JWT токена: {str(e)}")
            raise

# Функции для работы с паролями
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль хешу
    
    Args:
        plain_password: Обычный пароль
        hashed_password: Хешированный пароль
        
    Returns:
        bool: True, если пароль соответствует хешу
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля
    
    Args:
        password: Обычный пароль
        
    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)
