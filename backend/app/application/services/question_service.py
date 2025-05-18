from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.question import Question
from app.domain.schemas.question import (
    QuestionCreate, QuestionResponse, QuestionUpdate,
    QuestionListResponse, QuestionDetailResponse
)
from app.domain.schemas.vote import VoteTypeEnum as QuestionVoteSchema
from app.infrastructure.database.repositories import QuestionRepository, UserRepository
from app.infrastructure.cache.qa_cache import QACache

from .base import BaseService, NotFoundError, ValidationError, AuthorizationError

class QuestionService(BaseService):
    """Сервис для работы с вопросами"""
    
    def __init__(
        self,
        db: AsyncSession,
        qa_cache: Optional[QACache] = None
    ):
        super().__init__()
        self.db = db
        self.question_repository = QuestionRepository(db)
        self.qa_cache = qa_cache or QACache()
    
    async def create_question(self, data: QuestionCreate, author_id: int) -> Dict[str, Any]:
        """Создать новый вопрос"""
        try:
            question = await self.question_repository.create_question(
                obj_in=data.dict(),
                author_id=author_id
            )
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_questions_list()
            
            # Получаем полные данные вопроса
            question_data = await self.question_repository.get_with_details(question.id)
            return question_data
        except Exception as e:
            self._log_error("Ошибка при создании вопроса", e)
            raise

    async def update_question(self, question_id: int, data: QuestionUpdate, user_id: int) -> Dict[str, Any]:
        """Обновить вопрос"""
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем права
            if question.author_id != user_id:
                raise AuthorizationError("Редактирование вопроса")
            
            # Обновляем вопрос
            updated_question = await self.question_repository.update_question(
                db_obj=question,
                obj_in=data.dict(exclude_unset=True)
            )
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            await self.qa_cache.invalidate_questions_list()
            
            # Получаем полные данные вопроса
            question_data = await self.question_repository.get_with_details(updated_question.id)
            return question_data
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении вопроса {question_id}", e)
            raise
    
    async def delete_question(self, question_id: int, user_id: int) -> bool:
        """Удалить вопрос"""
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем права
            if question.author_id != user_id:
                raise AuthorizationError("Удаление вопроса")
            
            # Удаляем вопрос
            deleted = await self.question_repository.delete(question_id)
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            await self.qa_cache.invalidate_questions_list()
            
            return deleted
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении вопроса {question_id}", e)
            raise
    
    async def get_question(self, question_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить вопрос с деталями"""
        try:
            # Пробуем получить из кеша только для анонимных пользователей
            if not user_id:
                cached_question = await self.qa_cache.get_question(question_id)
                if cached_question:
                    return cached_question
            
            # Получаем вопрос из БД
            question = await self.question_repository.get_with_details(question_id, user_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Увеличиваем счетчик просмотров
            await self.question_repository.increment_view_count(question_id)
            
            # Сохраняем в кеш только для анонимных пользователей
            if not user_id:
                await self.qa_cache.set_question(question_id, question)
            
            return question
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при получении вопроса {question_id}", e)
            raise
    
    async def get_questions(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        plant_id: Optional[int] = None,
        author_id: Optional[int] = None,
        is_solved: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        user_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Получить список вопросов с фильтрацией и пагинацией"""
        try:
            # Пробуем получить из кеша только если нет user_id (для анонимных пользователей)
            if not user_id:
                cache_key = f"questions_{skip}_{limit}_{search}_{plant_id}_{author_id}_{is_solved}_{sort_by}_{sort_order}"
                cached_result = await self.qa_cache.get_questions_list(cache_key)
                if cached_result:
                    return cached_result
            
            # Получаем вопросы из БД (всегда передаем user_id для правильной загрузки связанных данных)
            questions, total = await self.question_repository.get_many_with_details(
                skip=skip,
                limit=limit,
                search=search,
                plant_id=plant_id,
                author_id=author_id,
                is_solved=is_solved,
                sort_by=sort_by,
                sort_order=sort_order,
                user_id=user_id
            )
            
            # Сохраняем в кеш только для анонимных пользователей
            if not user_id:
                cache_key = f"questions_{skip}_{limit}_{search}_{plant_id}_{author_id}_{is_solved}_{sort_by}_{sort_order}"
                await self.qa_cache.set_questions_list(cache_key, (questions, total))
            
            return questions, total
        except Exception as e:
            self._log_error("Ошибка при получении списка вопросов", e)
            raise
    
    async def vote_for_question(self, question_id: int, vote_data: Any, user_id: int) -> Dict[str, Any]:
        """Проголосовать за вопрос"""
        try:
            # Получаем vote_type из данных
            vote_type = vote_data.vote_type if hasattr(vote_data, 'vote_type') else vote_data
            
            # Проголосовать за вопрос
            success = await self.question_repository.vote_for_question(question_id, user_id, vote_type)
            if not success:
                raise ValidationError("Не удалось обработать голос за вопрос")
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            await self.qa_cache.invalidate_questions_list()
            
            # Возвращаем обновленный вопрос с деталями
            updated_question = await self.question_repository.get_with_details(question_id, user_id)
            return updated_question
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при голосовании за вопрос {question_id}", e)
            raise