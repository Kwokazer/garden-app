from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.question import Question
from app.domain.schemas.question import (
    QuestionCreate, QuestionResponse, QuestionUpdate,
    QuestionListResponse, QuestionDetailResponse
)
from app.domain.schemas.vote import VoteTypeEnum as QuestionVoteSchema
from app.infrastructure.database.repositories import QuestionRepository, TagRepository, UserRepository
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
        
        Args:
            data: Данные вопроса
            author_id: ID автора
            
        Returns:
            Dict[str, Any]: Созданный вопрос
        """
        try:
            # Создаем вопрос в БД
            question = await self.question_repository.create_with_tags(
                obj_in=data.dict(),
                author_id=author_id,
                tags=data.tags
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
        
        Args:
            question_id: ID вопроса
            data: Новые данные
            user_id: ID пользователя, который выполняет обновление
            
        Returns:
            Dict[str, Any]: Обновленный вопрос
            
        Raises:
            NotFoundError: Если вопрос не найден
            AuthorizationError: Если пользователь не имеет прав на обновление
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем права
            if question.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise AuthorizationError("Редактирование вопроса")
            
            # Обновляем вопрос
            updated_question = await self.question_repository.update_with_tags(
                db_obj=question,
                obj_in=data.dict(exclude_unset=True),
                tags=data.tags if data.tags is not None else None
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
        tag: Optional[str] = None,
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
            tag: Фильтр по тегу
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
            cache_key = f"questions_{skip}_{limit}_{search}_{tag}_{plant_id}_{author_id}_{is_solved}_{sort_by}_{sort_order}"
            cached_result = await self.qa_cache.get_questions_list(cache_key)
            if cached_result:
                return cached_result
            
            # Получаем вопросы из БД
            questions, total = await self.question_repository.get_many_with_details(
                skip=skip,
                limit=limit,
                search=search,
                tag=tag,
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
    
    async def vote_for_question(self, question_id: int, vote_data: QuestionVoteSchema, user_id: int) -> Dict[str, Any]:
        """
        Проголосовать за вопрос
        
        Args:
            question_id: ID вопроса
            vote_data: Данные голоса (up/down)
            user_id: ID пользователя, который голосует
            
        Returns:
            Dict[str, Any]: Обновленный вопрос
            
        Raises:
            NotFoundError: Если вопрос не найден
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError("Question", question_id)
            
            # Проверяем, не голосует ли пользователь за свой вопрос
            if question.author_id == user_id:
                raise ValidationError("Нельзя голосовать за свой собственный вопрос")
            
            # Добавляем голос
            vote_type = vote_data.vote_type
            await self._handle_question_vote(question_id, user_id, vote_type)
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            await self.qa_cache.invalidate_questions_list()
            
            # Получаем обновленный вопрос
            updated_question = await self.question_repository.get_with_details(question_id, user_id)
            return updated_question
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при голосовании за вопрос {question_id}", e)
            raise
    
    async def _handle_question_vote(self, question_id: int, user_id: int, vote_type: str) -> None:
        """
        Обработать голос за вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            vote_type: Тип голоса (up/down)
        """
        # Получаем текущий голос пользователя
        current_vote = await self.question_repository._get_user_vote(question_id, user_id)
        
        # Если голос такой же, удаляем его (отмена голоса)
        if current_vote == vote_type:
            await self.db.execute(f"""
                DELETE FROM question_votes
                WHERE question_id = {question_id} AND user_id = {user_id}
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_up = votes_up - 1
                    WHERE id = {question_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_down = votes_down - 1
                    WHERE id = {question_id}
                """)
        # Если голос противоположный, меняем его
        elif current_vote:
            await self.db.execute(f"""
                UPDATE question_votes
                SET vote_type = '{vote_type}'
                WHERE question_id = {question_id} AND user_id = {user_id}
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_up = votes_up + 1, votes_down = votes_down - 1
                    WHERE id = {question_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_up = votes_up - 1, votes_down = votes_down + 1
                    WHERE id = {question_id}
                """)
        # Если голоса нет, добавляем новый
        else:
            await self.db.execute(f"""
                INSERT INTO question_votes (question_id, user_id, vote_type)
                VALUES ({question_id}, {user_id}, '{vote_type}')
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_up = votes_up + 1
                    WHERE id = {question_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE questions
                    SET votes_down = votes_down + 1
                    WHERE id = {question_id}
                """) 