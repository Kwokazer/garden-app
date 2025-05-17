from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError

from app.domain.models.tag import Tag
from app.infrastructure.database.repositories.base import BaseRepository, DatabaseError

class TagRepository(BaseRepository[Tag]):
    """Репозиторий для работы с тегами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model_class=Tag)
    
    async def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        Получить все теги
        
        Returns:
            List[Dict[str, Any]]: Список тегов
        """
        try:
            # Используем чистый SQL запрос для обхода проблем совместимости SQLAlchemy 2.0
            result = await self.session.execute(text("SELECT id, name, description, created_at FROM tags ORDER BY name"))
            tags = []
            
            for row in result:
                tags.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3]
                })
            
            return tags
        except SQLAlchemyError as e:
            raise DatabaseError(f"Ошибка при получении всех тегов: {str(e)}")
    
    async def search_tags(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск тегов по части имени
        
        Args:
            query: Строка поиска
            limit: Максимальное количество результатов
            
        Returns:
            List[Dict[str, Any]]: Список найденных тегов
        """
        try:
            # Используем чистый SQL запрос с параметрами
            sql = text("SELECT id, name, description, created_at FROM tags WHERE name ILIKE :query ORDER BY name LIMIT :limit")
            result = await self.session.execute(sql, {"query": f"%{query}%", "limit": limit})
            
            tags = []
            for row in result:
                tags.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3]
                })
            
            return tags
        except SQLAlchemyError as e:
            raise DatabaseError(f"Ошибка при поиске тегов: {str(e)}")
    
    async def create_tag(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Создать новый тег
        
        Args:
            name: Имя тега
            description: Описание тега
            
        Returns:
            Dict[str, Any]: Созданный тег
        """
        try:
            # Проверяем, существует ли тег с таким именем
            result = await self.session.execute(
                text("SELECT id FROM tags WHERE LOWER(name) = LOWER(:name)"), 
                {"name": name}
            )
            existing_tag = result.first()
            
            if existing_tag:
                # Если тег существует, получаем его
                result = await self.session.execute(
                    text("SELECT id, name, description, created_at FROM tags WHERE id = :id"),
                    {"id": existing_tag[0]}
                )
                row = result.first()
                return {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "created_at": row[3]
                }
            
            # Создаем новый тег
            tag = Tag(name=name, description=description)
            self.session.add(tag)
            await self.session.flush()
            
            return {
                "id": tag.id,
                "name": tag.name,
                "description": tag.description,
                "created_at": tag.created_at
            }
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Ошибка при создании тега: {str(e)}") 