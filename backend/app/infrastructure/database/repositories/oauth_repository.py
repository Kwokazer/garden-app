import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.oauth_account import OAuthAccount

from .base import BaseRepository, DatabaseError, EntityNotFoundError

logger = logging.getLogger(__name__)

class OAuthRepository(BaseRepository[OAuthAccount]):
    """Репозиторий для работы с OAuth аккаунтами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, OAuthAccount)
    
    async def get_by_provider_and_id(self, provider: str, provider_user_id: str) -> Optional[OAuthAccount]:
        """Получить OAuth аккаунт по провайдеру и ID пользователя у провайдера"""
        try:
            query = select(OAuthAccount).where(
                and_(
                    OAuthAccount.provider == provider,
                    OAuthAccount.provider_user_id == provider_user_id
                )
            )
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении OAuth аккаунта: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_by_user_id(self, user_id: int) -> List[OAuthAccount]:
        """Получить все OAuth аккаунты пользователя"""
        try:
            query = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении OAuth аккаунтов пользователя: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_by_user_and_provider(self, user_id: int, provider: str) -> Optional[OAuthAccount]:
        """Получить OAuth аккаунт пользователя по провайдеру"""
        try:
            query = select(OAuthAccount).where(
                and_(
                    OAuthAccount.user_id == user_id,
                    OAuthAccount.provider == provider
                )
            )
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении OAuth аккаунта пользователя: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def update_tokens(self, account_id: int, access_token: str, refresh_token: Optional[str], expires_at: Optional[datetime]) -> OAuthAccount:
        """Обновить токены для OAuth аккаунта"""
        try:
            account = await self.get_by_id(account_id)
            
            account.access_token = access_token
            if refresh_token:
                account.refresh_token = refresh_token
            if expires_at:
                account.expires_at = expires_at
                
            await self.session.flush()
            return account
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при обновлении токенов: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def is_token_expired(self, account_id: int) -> bool:
        """Проверить, истек ли токен для аккаунта"""
        try:
            account = await self.get_by_id(account_id)
            
            if not account.expires_at:
                return False  # Если нет времени истечения, считаем, что токен не истекает
                
            return account.expires_at < datetime.utcnow()
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке срока действия токена: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
        
    async def delete_by_user_and_provider(self, user_id: int, provider: str) -> bool:
        """Удалить OAuth аккаунт пользователя по провайдеру"""
        try:
            account = await self.get_by_user_and_provider(user_id, provider)
            if not account:
                return False
                
            await self.session.delete(account)
            await self.session.flush()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении OAuth аккаунта: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}") 