from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.base import (
    BaseRepository, DatabaseError, EntityNotFoundError, UniqueConstraintError)
from app.infrastructure.database.repositories.oauth_repository import \
    OAuthRepository
from app.infrastructure.database.repositories.plant_repository import PlantRepository
from app.infrastructure.database.repositories.plant_category_repository import \
    PlantCategoryRepository
from app.infrastructure.database.repositories.climate_zone_repository import \
    ClimateZoneRepository
from app.infrastructure.database.repositories.role_repository import \
    RoleRepository
from app.infrastructure.database.repositories.user_repository import \
    UserRepository
from app.infrastructure.database.repositories.question_repository import QuestionRepository
from app.infrastructure.database.repositories.answer_repository import AnswerRepository
from app.infrastructure.database.repositories.tag_repository import TagRepository

# Типы репозиториев
REPOSITORY_TYPES = {
    "user": UserRepository,
    "role": RoleRepository,
    "oauth": OAuthRepository,
    "plant": PlantRepository,
    "plant_category": PlantCategoryRepository,
    "climate_zone": ClimateZoneRepository,
    "question": QuestionRepository,
    "answer": AnswerRepository,
    "tag": TagRepository,
}

def get_repository(repo_type: str, session: AsyncSession) -> BaseRepository:
    """
    Фабричный метод для получения репозитория по типу
    
    Args:
        repo_type: Тип репозитория из REPOSITORY_TYPES
        session: Асинхронная сессия SQLAlchemy
        
    Returns:
        Экземпляр запрошенного репозитория
    
    Raises:
        ValueError: Если запрошенный тип репозитория не существует
    """
    repo_class = REPOSITORY_TYPES.get(repo_type)
    if not repo_class:
        valid_types = ", ".join(REPOSITORY_TYPES.keys())
        raise ValueError(f"Неизвестный тип репозитория: {repo_type}. Допустимые типы: {valid_types}")
    
    return repo_class(session)

__all__ = [
    "BaseRepository",
    "EntityNotFoundError",
    "UniqueConstraintError",
    "DatabaseError",
    "UserRepository",
    "RoleRepository",
    "OAuthRepository",
    "PlantRepository",
    "PlantCategoryRepository",
    "ClimateZoneRepository",
    "get_repository",
    "REPOSITORY_TYPES",
    "QuestionRepository",
    "AnswerRepository",
    "TagRepository",
] 