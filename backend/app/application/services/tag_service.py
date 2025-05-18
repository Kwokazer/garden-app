from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.base import (BaseService, NotFoundError,
                                           ValidationError)
from app.domain.models.tag import Tag
from app.domain.schemas.tag import (TagCreate, TagResponse, TagUpdate)
from app.infrastructure.database.repositories.tag_repository import TagRepository


class TagService(BaseService):
    """
    Сервис для работы с тегами
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.tag_repository = TagRepository(session)
    
    async def get_tags(self, skip: int = 0, limit: int = 50) -> List[TagResponse]:
        """
        Получить список тегов
        """
        try:
            tags = await self.tag_repository.get_tags(skip, limit)
            return [TagResponse.model_validate(tag) for tag in tags]
        except Exception as e:
            self._log_error(f"Ошибка при получении списка тегов: {str(e)}", e)
            raise ValidationError(f"Не удалось получить список тегов: {str(e)}")
    
    async def get_tag(self, tag_id: int) -> TagResponse:
        """
        Получить тег по ID
        """
        try:
            tag = await self.tag_repository.get_tag(tag_id)
            return TagResponse.model_validate(tag)
        except Exception as e:
            self._log_error(f"Ошибка при получении тега с ID {tag_id}: {str(e)}", e)
            raise NotFoundError("Tag", tag_id)
    
    async def search_tags(self, query: str, skip: int = 0, limit: int = 20) -> List[TagResponse]:
        """
        Поиск тегов по названию
        """
        try:
            tags = await self.tag_repository.search_tags(query, skip, limit)
            return [TagResponse.model_validate(tag) for tag in tags]
        except Exception as e:
            self._log_error(f"Ошибка при поиске тегов: {str(e)}", e)
            raise ValidationError(f"Не удалось выполнить поиск тегов: {str(e)}")
    
    async def create_tag(self, tag_data: TagCreate) -> TagResponse:
        """
        Создать новый тег
        """
        try:
            # Проверяем, что тег с таким именем еще не существует
            existing_tag = await self.tag_repository.get_tag_by_name(tag_data.name)
            if existing_tag:
                raise ValidationError(f"Тег с именем '{tag_data.name}' уже существует")
            
            # Создаем тег
            create_data = tag_data.model_dump()
            tag = await self.tag_repository.create(create_data)
            
            return TagResponse.model_validate(tag)
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при создании тега: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось создать тег: {str(e)}")
    
    async def update_tag(self, tag_id: int, tag_data: TagUpdate) -> TagResponse:
        """
        Обновить тег
        """
        try:
            # Проверяем, что тег существует
            existing_tag = await self.tag_repository.get_tag(tag_id)
            
            # Если меняется имя, проверяем, что оно не конфликтует с другими тегами
            if tag_data.name and tag_data.name != existing_tag.name:
                name_check = await self.tag_repository.get_tag_by_name(tag_data.name)
                if name_check:
                    raise ValidationError(f"Тег с именем '{tag_data.name}' уже существует")
            
            # Обновляем тег
            update_data = tag_data.model_dump(exclude_unset=True)
            tag = await self.tag_repository.update(tag_id, update_data)
            
            return TagResponse.model_validate(tag)
        except NotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении тега с ID {tag_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось обновить тег: {str(e)}")
    
    async def delete_tag(self, tag_id: int) -> bool:
        """
        Удалить тег
        """
        try:
            # Проверяем, что тег существует
            await self.tag_repository.get_tag(tag_id)
            
            # Удаляем тег
            result = await self.tag_repository.delete(tag_id)
            return result
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении тега с ID {tag_id}: {str(e)}", e)
            await self.session.rollback()
            raise ValidationError(f"Не удалось удалить тег: {str(e)}")