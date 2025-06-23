import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.webinar import Webinar, WebinarStatus
from app.infrastructure.database.repositories.base import BaseRepository, DatabaseError, EntityNotFoundError

logger = logging.getLogger(__name__)

class WebinarRepository(BaseRepository[Webinar]):
    """Репозиторий для работы с вебинарами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Webinar)
    
    async def get_webinars_to_activate(self, current_time: datetime) -> List[Webinar]:
        """
        Получить вебинары, которые должны быть активированы
        (время наступило, но статус еще SCHEDULED)
        """
        try:
            stmt = (
                select(Webinar)
                .where(
                    and_(
                        Webinar.scheduled_at <= current_time,
                        Webinar.status == WebinarStatus.SCHEDULED
                    )
                )
                .order_by(Webinar.scheduled_at)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении вебинаров для активации: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_by_room_name(self, room_name: str) -> Optional[Webinar]:
        """Получить вебинар по имени комнаты"""
        return await self.get_by_field("room_name", room_name)
    
    async def get_webinars_by_host(self, host_id: int, skip: int = 0, limit: int = 100) -> List[Webinar]:
        """Получить вебинары по ID ведущего"""
        try:
            stmt = (
                select(Webinar)
                .where(Webinar.host_id == host_id)
                .order_by(Webinar.scheduled_at.desc())
                .offset(skip)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении вебинаров ведущего {host_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_webinars_by_status(self, status: WebinarStatus, skip: int = 0, limit: int = 100) -> List[Webinar]:
        """Получить вебинары по статусу"""
        try:
            stmt = (
                select(Webinar)
                .where(Webinar.status == status)
                .order_by(Webinar.scheduled_at.desc())
                .offset(skip)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении вебинаров со статусом {status}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_upcoming_webinars(self, current_time: datetime, skip: int = 0, limit: int = 100) -> List[Webinar]:
        """Получить предстоящие вебинары"""
        try:
            stmt = (
                select(Webinar)
                .where(
                    and_(
                        Webinar.scheduled_at > current_time,
                        Webinar.status == WebinarStatus.SCHEDULED
                    )
                )
                .order_by(Webinar.scheduled_at.asc())
                .offset(skip)
                .limit(limit)
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении предстоящих вебинаров: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_live_webinars(self) -> List[Webinar]:
        """Получить активные (LIVE) вебинары"""
        try:
            stmt = (
                select(Webinar)
                .where(Webinar.status == WebinarStatus.LIVE)
                .order_by(Webinar.scheduled_at.desc())
            )
            
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении активных вебинаров: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
