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
        """
        Создать новый вопрос
        """
        try:
            # Заменить create_with_tags на create_question
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
        """
        Обновить вопрос
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем права
            if question.author_id != user_id:
                raise AuthorizationError("Редактирование вопроса")
            
            # Заменить update_with_tags на update_question
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
        """
        Удалить вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя, который выполняет удаление
            
        Returns:
            bool: True, если вопрос успешно удален
            
        Raises:
            NotFoundError: Если вопрос не найден
            AuthorizationError: Если пользователь не имеет прав на удаление
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем права
            if question.author_id != user_id:
                # TODO: Добавить проверку администратора
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
        """
        Получить вопрос с деталями
        
        Args:
            question_id: ID вопроса
            user_id: ID текущего пользователя
            
        Returns:
            Dict[str, Any]: Вопрос с деталями
            
        Raises:
            NotFoundError: Если вопрос не найден
        """
        try:
            # Пробуем получить из кеша
            cached_question = await self.qa_cache.get_question(question_id)
            if cached_question:
                return cached_question
            
            # Получаем вопрос из БД
            question = await self.question_repository.get_with_details(question_id, user_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Увеличиваем счетчик просмотров
            await self.question_repository.increment_view_count(question_id)
            
            # Сохраняем в кеш
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
        """
        Получить список вопросов с фильтрацией и пагинацией
        
        Args:
            skip: Смещение для пагинации
            limit: Лимит для пагинации
            search: Строка поиска
            plant_id: Фильтр по ID растения
            author_id: Фильтр по ID автора
            is_solved: Фильтр по статусу решения
            sort_by: Поле для сортировки
            sort_order: Порядок сортировки (asc/desc)
            user_id: ID текущего пользователя
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: Список вопросов и общее количество
        """
        try:
            # Пробуем получить из кеша
            cache_key = f"questions_{skip}_{limit}_{search}_{plant_id}_{author_id}_{is_solved}_{sort_by}_{sort_order}"
            cached_result = await self.qa_cache.get_questions_list(cache_key)
            if cached_result:
                return cached_result
            
            # Получаем вопросы из БД
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
            
            # Сохраняем в кеш
            await self.qa_cache.set_questions_list(cache_key, (questions, total))
            
            return questions, total
        except Exception as e:
            self._log_error("Ошибка при получении списка вопросов", e)
            raise
    
    async def vote_for_question(self, question_id: int, user_id: int, vote_type: str) -> bool:
        """
        Проголосовать за вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            vote_type: Тип голоса (up/down)
            
        Returns:
            bool: True, если голос успешно добавлен/изменен/удален
        """
        try:
            from app.domain.models.vote import QuestionVote
            
            # Проверяем существующий голос
            existing_vote_stmt = select(QuestionVote).where(
                and_(
                    QuestionVote.question_id == question_id,
                    QuestionVote.user_id == user_id
                )
            )
            result = await self.session.execute(existing_vote_stmt)
            existing_vote = result.scalars().first()
            
            question = await self.get(question_id)
            if not question:
                raise EntityNotFoundError("Question", question_id)
            
            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Удаляем голос (отмена)
                    await self.session.delete(existing_vote)
                    if vote_type == "up":
                        question.votes_up = max(0, question.votes_up - 1)
                    else:
                        question.votes_down = max(0, question.votes_down - 1)
                else:
                    # Меняем тип голоса
                    existing_vote.vote_type = vote_type
                    if vote_type == "up":
                        question.votes_up += 1
                        question.votes_down = max(0, question.votes_down - 1)
                    else:
                        question.votes_down += 1
                        question.votes_up = max(0, question.votes_up - 1)
            else:
                # Добавляем новый голос
                new_vote = QuestionVote(
                    question_id=question_id,
                    user_id=user_id,
                    vote_type=vote_type
                )
                self.session.add(new_vote)
                if vote_type == "up":
                    question.votes_up += 1
                else:
                    question.votes_down += 1
            
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Ошибка при голосовании за вопрос: {str(e)}")
    
    async def _handle_question_vote(self, question_id: int, user_id: int, vote_type: str) -> None:
        """
        Обработать голос за вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            vote_type: Тип голоса (up/down)
        """
        success = await self.question_repository.vote_for_question(question_id, user_id, vote_type)
        if not success:
            raise ValidationError("Не удалось обработать голос за вопрос")