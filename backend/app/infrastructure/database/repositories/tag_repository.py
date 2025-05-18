from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.tag import Tag
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError

class TagRepository(BaseRepository[Tag]):
    """Репозиторий для работы с тегами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Tag)
    
    async def get_tags(self, skip: int = 0, limit: int = 100) -> List[Tag]:
        """
        Получить список тегов с пагинацией
        """
        query = select(Tag).offset(skip).limit(limit).order_by(Tag.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_tag(self, tag_id: int) -> Tag:
        """
        Получить тег по ID
        """
        query = select(Tag).filter(Tag.id == tag_id)
        result = await self.session.execute(query)
        tag = result.scalars().first()
        
        if not tag:
            raise EntityNotFoundError("Tag", tag_id)
        
        return tag
    
    async def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """
        Получить тег по имени
        """
        query = select(Tag).filter(Tag.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def search_tags(self, query_text: str, skip: int = 0, limit: int = 20) -> List[Tag]:
        """
        Поиск тегов по названию
        """
        search_query = f"%{query_text.lower()}%"
        query = (
            select(Tag)
            .filter(func.lower(Tag.name).like(search_query))
            .offset(skip)
            .limit(limit)
            .order_by(Tag.name)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_tags(self) -> int:
        """
        Получить общее количество тегов
        """
        query = select(func.count()).select_from(Tag)
        result = await self.session.execute(query)
        return result.scalar() or 0