import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.base import Base, BaseModel

# Типовая переменная для моделей ORM
T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)

class RepositoryError(Exception):
    """Базовый класс для ошибок репозитория"""
    pass

class EntityNotFoundError(RepositoryError):
    """Выбрасывается, когда сущность не найдена"""
    def __init__(self, entity_type: str, entity_id: Any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} с ID {entity_id} не найден")

class UniqueConstraintError(RepositoryError):
    """Выбрасывается при нарушении ограничения уникальности"""
    def __init__(self, entity_type: str, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(f"{entity_type} с {field}={value} уже существует")

class DatabaseError(RepositoryError):
    """Выбрасывается при общих ошибках базы данных"""
    pass

class BaseRepository(Generic[T]):
    """Базовый репозиторий, содержащий общие методы CRUD для всех моделей"""
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
        
    async def get_by_id(self, entity_id: int) -> T:
        """Получить сущность по ID"""
        try:
            query = select(self.model_class).where(self.model_class.id == entity_id)
            result = await self.session.execute(query)
            entity = result.scalars().first()
            
            if entity is None:
                entity_name = self.model_class.__name__
                raise EntityNotFoundError(entity_name, entity_id)
                
            return entity
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении {self.model_class.__name__} по ID {entity_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def get_all(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[T]:
        """Получить все сущности с пагинацией и фильтрацией"""
        try:
            query = select(self.model_class)
            
            # Применяем фильтры, если они есть
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.where(getattr(self.model_class, field) == value)
            
            query = query.offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении списка {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Получить количество сущностей с фильтрацией"""
        try:
            query = select(func.count(self.model_class.id))
            
            # Применяем фильтры, если они есть
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model_class, field):
                        query = query.where(getattr(self.model_class, field) == value)
            
            result = await self.session.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при подсчёте {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Создать новую сущность"""
        try:
            entity = self.model_class(**data)
            self.session.add(entity)
            await self.session.flush()
            return entity
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка целостности при создании {self.model_class.__name__}: {str(e)}")
            if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                # Пытаемся определить, какое поле вызвало ограничение уникальности
                field = self._extract_field_from_integrity_error(str(e))
                value = data.get(field, 'значение')
                raise UniqueConstraintError(self.model_class.__name__, field, value)
            raise DatabaseError(f"Ошибка целостности базы данных: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при создании {self.model_class.__name__}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def update(self, entity_id: int, data: Dict[str, Any]) -> T:
        """Обновить существующую сущность"""
        try:
            entity = await self.get_by_id(entity_id)
            
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            await self.session.flush()
            return entity
        except EntityNotFoundError:
            raise
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Ошибка целостности при обновлении {self.model_class.__name__} с ID {entity_id}: {str(e)}")
            if 'unique constraint' in str(e).lower() or 'duplicate key' in str(e).lower():
                field = self._extract_field_from_integrity_error(str(e))
                value = data.get(field, 'значение')
                raise UniqueConstraintError(self.model_class.__name__, field, value)
            raise DatabaseError(f"Ошибка целостности базы данных: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при обновлении {self.model_class.__name__} с ID {entity_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    async def delete(self, entity_id: int) -> bool:
        """Удалить сущность по ID"""
        try:
            # Сначала проверяем, существует ли сущность
            entity = await self.get_by_id(entity_id)
            
            # Удаляем сущность
            await self.session.delete(entity)
            await self.session.flush()
            return True
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка при удалении {self.model_class.__name__} с ID {entity_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
        
    async def exists(self, entity_id: int) -> bool:
        """Проверить, существует ли сущность с указанным ID"""
        try:
            query = select(func.count(self.model_class.id)).where(self.model_class.id == entity_id)
            result = await self.session.execute(query)
            return result.scalar() > 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке существования {self.model_class.__name__} с ID {entity_id}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
        
    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Найти сущность по значению поля"""
        try:
            if not hasattr(self.model_class, field):
                raise ValueError(f"Поле {field} не существует в модели {self.model_class.__name__}")
                
            query = select(self.model_class).where(getattr(self.model_class, field) == value)
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске {self.model_class.__name__} по полю {field}: {str(e)}")
            raise DatabaseError(f"Ошибка базы данных: {str(e)}")
    
    def _extract_field_from_integrity_error(self, error_message: str) -> str:
        """Попытка извлечь имя поля из сообщения об ошибке IntegrityError"""
        # Этот метод нужно адаптировать для конкретной СУБД
        # Пример для PostgreSQL
        if 'key (email)' in error_message:
            return 'email'
        if 'key (username)' in error_message:
            return 'username'
        if 'key (verification_token)' in error_message:
            return 'verification_token'
        if 'key (reset_token)' in error_message:
            return 'reset_token'
        
        # Предполагаем, что в ошибке может быть имя ограничения
        constraints = {
            'uq_provider_account': 'provider/provider_user_id',
            'uq_users_email': 'email',
            'uq_users_username': 'username',
            'uq_users_verification_token': 'verification_token',
            'uq_users_reset_token': 'reset_token'
        }
            
        for constraint_name, field in constraints.items():
            if constraint_name in error_message:
                return field
        
        return 'unknown_field'

# Вспомогательные функции для преобразования ошибок репозитория в HTTP-исключения
def handle_repository_error(error: Exception) -> None:
    """Преобразует ошибки репозитория в HTTP-исключения FastAPI"""
    if isinstance(error, EntityNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    elif isinstance(error, UniqueConstraintError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )
    elif isinstance(error, DatabaseError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при работе с базой данных"
        )
    elif isinstance(error, RepositoryError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    else:
        # Для неизвестных ошибок - 500
        logger.exception("Необработанная ошибка в репозитории")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        ) 