from typing import List, Optional, Dict, Any, Tuple
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.qa import Question, Answer
from app.domain.schemas.qa import (
    QuestionCreate, QuestionUpdate, QuestionWithAuthor, QuestionWithDetails,
    AnswerCreate, AnswerUpdate, AnswerWithAuthor, AnswerWithDetails, 
    QuestionVote as QuestionVoteSchema, AnswerVote as AnswerVoteSchema
)
from app.infrastructure.database import get_db
from app.infrastructure.database.repositories.question_repository import QuestionRepository
from app.infrastructure.database.repositories.answer_repository import AnswerRepository
from app.infrastructure.cache.qa_cache import QACache

from .base import BaseService, NotFoundError, ValidationError

class QAService(BaseService):
    """Сервис для работы с вопросами и ответами"""
    
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        qa_cache: Optional[QACache] = None
    ):
        super().__init__()
        self.db = db
        self.question_repository = QuestionRepository(db)
        self.answer_repository = AnswerRepository(db)
        self.qa_cache = qa_cache or QACache()
    
    # --------- Методы для работы с вопросами ---------
    
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
            PermissionError: Если пользователь не имеет прав на обновление
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError(f"Вопрос с ID {question_id} не найден")
            
            # Проверяем права
            if question.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise PermissionError("У вас нет прав на обновление этого вопроса")
            
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
        except (NotFoundError, PermissionError):
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
            PermissionError: Если пользователь не имеет прав на удаление
        """
        try:
            # Получаем вопрос
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError(f"Вопрос с ID {question_id} не найден")
            
            # Проверяем права
            if question.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise PermissionError("У вас нет прав на удаление этого вопроса")
            
            # Удаляем вопрос
            deleted = await self.question_repository.delete(question_id)
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            await self.qa_cache.invalidate_questions_list()
            
            return deleted
        except (NotFoundError, PermissionError):
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
                raise NotFoundError(f"Вопрос с ID {question_id} не найден")
            
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
            # Проверяем наличие в кеше для простых запросов
            if not search and not tag and not plant_id and not author_id and is_solved is None:
                cache_key = f"questions:{skip}:{limit}:{sort_by}:{sort_order}"
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
            
            # Кешируем результат для простых запросов
            if not search and not tag and not plant_id and not author_id and is_solved is None:
                cache_key = f"questions:{skip}:{limit}:{sort_by}:{sort_order}"
                await self.qa_cache.set_questions_list(cache_key, (questions, total))
            
            return questions, total
        except Exception as e:
            self._log_error("Ошибка при получении списка вопросов", e)
            raise
    
    async def vote_for_question(self, question_id: int, vote_data: QuestionVoteSchema, user_id: int) -> Dict[str, Any]:
        """
        Голосовать за вопрос
        
        Args:
            question_id: ID вопроса
            vote_data: Данные голосования
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Обновленный вопрос
            
        Raises:
            NotFoundError: Если вопрос не найден
            ValidationError: При ошибке валидации
        """
        try:
            # Проверяем существование вопроса
            question = await self.question_repository.get(question_id)
            if not question:
                raise NotFoundError(f"Вопрос с ID {question_id} не найден")
            
            # Получаем текущий голос пользователя
            from app.domain.models.qa import QuestionVote
            stmt = (
                select(QuestionVote)
                .where(
                    and_(
                        QuestionVote.question_id == question_id,
                        QuestionVote.user_id == user_id
                    )
                )
            )
            result = await self.db.execute(stmt)
            existing_vote = result.scalars().first()
            
            # Логика голосования
            if existing_vote:
                if existing_vote.vote_type == vote_data.vote_type:
                    # Отмена голоса
                    await self.db.delete(existing_vote)
                    
                    # Обновляем счетчики
                    if vote_data.vote_type == "upvote":
                        question.votes_up = max(0, question.votes_up - 1)
                    else:
                        question.votes_down = max(0, question.votes_down - 1)
                else:
                    # Изменение типа голоса
                    existing_vote.vote_type = vote_data.vote_type
                    self.db.add(existing_vote)
                    
                    # Обновляем счетчики
                    if vote_data.vote_type == "upvote":
                        question.votes_up += 1
                        question.votes_down = max(0, question.votes_down - 1)
                    else:
                        question.votes_down += 1
                        question.votes_up = max(0, question.votes_up - 1)
            else:
                # Новый голос
                new_vote = QuestionVote(
                    question_id=question_id,
                    user_id=user_id,
                    vote_type=vote_data.vote_type
                )
                self.db.add(new_vote)
                
                # Обновляем счетчики
                if vote_data.vote_type == "upvote":
                    question.votes_up += 1
                else:
                    question.votes_down += 1
            
            # Сохраняем изменения
            self.db.add(question)
            await self.db.commit()
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            
            # Получаем обновленные данные
            updated_question = await self.question_repository.get_with_details(question_id, user_id)
            return updated_question
        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self._log_error(f"Ошибка при голосовании за вопрос {question_id}", e)
            raise
    
    # --------- Методы для работы с ответами ---------
    
    async def create_answer(self, data: AnswerCreate, author_id: int) -> Dict[str, Any]:
        """
        Создать новый ответ
        
        Args:
            data: Данные ответа
            author_id: ID автора
            
        Returns:
            Dict[str, Any]: Созданный ответ
            
        Raises:
            NotFoundError: Если вопрос не найден
        """
        try:
            # Проверяем существование вопроса
            question = await self.question_repository.get(data.question_id)
            if not question:
                raise NotFoundError(f"Вопрос с ID {data.question_id} не найден")
            
            # Создаем ответ
            answer = await self.answer_repository.create_answer(
                question_id=data.question_id,
                body=data.body,
                author_id=author_id
            )
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(data.question_id)
            
            # Получаем данные с автором
            from sqlalchemy.orm import joinedload
            stmt = (
                select(Answer)
                .options(joinedload(Answer.author))
                .where(Answer.id == answer.id)
            )
            result = await self.db.execute(stmt)
            answer_with_author = result.scalars().first()
            
            # Преобразуем в словарь
            return {
                "id": answer_with_author.id,
                "body": answer_with_author.body,
                "created_at": answer_with_author.created_at,
                "updated_at": answer_with_author.updated_at,
                "author_id": answer_with_author.author_id,
                "question_id": answer_with_author.question_id,
                "is_accepted": answer_with_author.is_accepted,
                "votes_up": answer_with_author.votes_up,
                "votes_down": answer_with_author.votes_down,
                "author": {
                    "id": answer_with_author.author.id,
                    "username": answer_with_author.author.username,
                    "avatar_url": answer_with_author.author.avatar_url
                }
            }
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error(f"Ошибка при создании ответа для вопроса {data.question_id}", e)
            raise
    
    async def update_answer(self, answer_id: int, data: AnswerUpdate, user_id: int) -> Dict[str, Any]:
        """
        Обновить ответ
        
        Args:
            answer_id: ID ответа
            data: Новые данные
            user_id: ID пользователя, который выполняет обновление
            
        Returns:
            Dict[str, Any]: Обновленный ответ
            
        Raises:
            NotFoundError: Если ответ не найден
            PermissionError: Если пользователь не имеет прав на обновление
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError(f"Ответ с ID {answer_id} не найден")
            
            # Проверяем права
            if answer.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise PermissionError("У вас нет прав на обновление этого ответа")
            
            # Обновляем ответ
            updated_answer = await self.answer_repository.update_answer(
                db_obj=answer,
                body=data.body
            )
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(answer.question_id)
            
            # Получаем данные с автором
            from sqlalchemy.orm import joinedload
            stmt = (
                select(Answer)
                .options(joinedload(Answer.author))
                .where(Answer.id == updated_answer.id)
            )
            result = await self.db.execute(stmt)
            answer_with_author = result.scalars().first()
            
            # Преобразуем в словарь
            return {
                "id": answer_with_author.id,
                "body": answer_with_author.body,
                "created_at": answer_with_author.created_at,
                "updated_at": answer_with_author.updated_at,
                "author_id": answer_with_author.author_id,
                "question_id": answer_with_author.question_id,
                "is_accepted": answer_with_author.is_accepted,
                "votes_up": answer_with_author.votes_up,
                "votes_down": answer_with_author.votes_down,
                "author": {
                    "id": answer_with_author.author.id,
                    "username": answer_with_author.author.username,
                    "avatar_url": answer_with_author.author.avatar_url
                }
            }
        except (NotFoundError, PermissionError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при обновлении ответа {answer_id}", e)
            raise
    
    async def delete_answer(self, answer_id: int, user_id: int) -> bool:
        """
        Удалить ответ
        
        Args:
            answer_id: ID ответа
            user_id: ID пользователя, который выполняет удаление
            
        Returns:
            bool: True, если ответ успешно удален
            
        Raises:
            NotFoundError: Если ответ не найден
            PermissionError: Если пользователь не имеет прав на удаление
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError(f"Ответ с ID {answer_id} не найден")
            
            # Проверяем права
            if answer.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise PermissionError("У вас нет прав на удаление этого ответа")
            
            # Запоминаем ID вопроса для инвалидации кеша
            question_id = answer.question_id
            
            # Удаляем ответ
            deleted = await self.answer_repository.delete(answer_id)
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(question_id)
            
            return deleted
        except (NotFoundError, PermissionError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении ответа {answer_id}", e)
            raise
    
    async def mark_answer_as_accepted(self, answer_id: int, user_id: int) -> Dict[str, Any]:
        """
        Отметить ответ как принятый
        
        Args:
            answer_id: ID ответа
            user_id: ID пользователя, который выполняет действие
            
        Returns:
            Dict[str, Any]: Обновленный ответ
            
        Raises:
            NotFoundError: Если ответ не найден
            PermissionError: Если пользователь не имеет прав
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError(f"Ответ с ID {answer_id} не найден")
            
            # Получаем вопрос
            question = await self.question_repository.get(answer.question_id)
            if not question:
                raise NotFoundError(f"Вопрос с ID {answer.question_id} не найден")
            
            # Проверяем права (только автор вопроса может принимать ответы)
            if question.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise PermissionError("Только автор вопроса может принимать ответы")
            
            # Отмечаем ответ как принятый
            success = await self.answer_repository.mark_as_accepted(answer_id, answer.question_id)
            if not success:
                raise ValidationError("Не удалось отметить ответ как принятый")
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(answer.question_id)
            await self.qa_cache.invalidate_questions_list()
            
            # Получаем обновленный ответ
            updated_answer = await self.answer_repository.get(answer_id)
            
            # Получаем данные с автором
            from sqlalchemy.orm import joinedload
            stmt = (
                select(Answer)
                .options(joinedload(Answer.author))
                .where(Answer.id == updated_answer.id)
            )
            result = await self.db.execute(stmt)
            answer_with_author = result.scalars().first()
            
            # Преобразуем в словарь
            return {
                "id": answer_with_author.id,
                "body": answer_with_author.body,
                "created_at": answer_with_author.created_at,
                "updated_at": answer_with_author.updated_at,
                "author_id": answer_with_author.author_id,
                "question_id": answer_with_author.question_id,
                "is_accepted": answer_with_author.is_accepted,
                "votes_up": answer_with_author.votes_up,
                "votes_down": answer_with_author.votes_down,
                "author": {
                    "id": answer_with_author.author.id,
                    "username": answer_with_author.author.username,
                    "avatar_url": answer_with_author.author.avatar_url
                }
            }
        except (NotFoundError, PermissionError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при отметке ответа {answer_id} как принятого", e)
            raise
    
    async def vote_for_answer(self, answer_id: int, vote_data: AnswerVoteSchema, user_id: int) -> Dict[str, Any]:
        """
        Голосовать за ответ
        
        Args:
            answer_id: ID ответа
            vote_data: Данные голосования
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Обновленный ответ
            
        Raises:
            NotFoundError: Если ответ не найден
            ValidationError: При ошибке валидации
        """
        try:
            # Проверяем существование ответа
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError(f"Ответ с ID {answer_id} не найден")
            
            # Получаем текущий голос пользователя
            from app.domain.models.qa import AnswerVote
            from sqlalchemy import select, and_
            stmt = (
                select(AnswerVote)
                .where(
                    and_(
                        AnswerVote.answer_id == answer_id,
                        AnswerVote.user_id == user_id
                    )
                )
            )
            result = await self.db.execute(stmt)
            existing_vote = result.scalars().first()
            
            # Логика голосования
            if existing_vote:
                if existing_vote.vote_type == vote_data.vote_type:
                    # Отмена голоса
                    await self.db.delete(existing_vote)
                    
                    # Обновляем счетчики
                    if vote_data.vote_type == "upvote":
                        answer.votes_up = max(0, answer.votes_up - 1)
                    else:
                        answer.votes_down = max(0, answer.votes_down - 1)
                else:
                    # Изменение типа голоса
                    existing_vote.vote_type = vote_data.vote_type
                    self.db.add(existing_vote)
                    
                    # Обновляем счетчики
                    if vote_data.vote_type == "upvote":
                        answer.votes_up += 1
                        answer.votes_down = max(0, answer.votes_down - 1)
                    else:
                        answer.votes_down += 1
                        answer.votes_up = max(0, answer.votes_up - 1)
            else:
                # Новый голос
                new_vote = AnswerVote(
                    answer_id=answer_id,
                    user_id=user_id,
                    vote_type=vote_data.vote_type
                )
                self.db.add(new_vote)
                
                # Обновляем счетчики
                if vote_data.vote_type == "upvote":
                    answer.votes_up += 1
                else:
                    answer.votes_down += 1
            
            # Сохраняем изменения
            self.db.add(answer)
            await self.db.commit()
            
            # Инвалидируем кеш
            await self.qa_cache.invalidate_question(answer.question_id)
            
            # Получаем данные с автором
            from sqlalchemy.orm import joinedload
            stmt = (
                select(Answer)
                .options(joinedload(Answer.author))
                .where(Answer.id == answer.id)
            )
            result = await self.db.execute(stmt)
            answer_with_author = result.scalars().first()
            
            # Получаем тип голоса пользователя
            user_vote = await self.answer_repository._get_user_vote(answer_id, user_id)
            
            # Преобразуем в словарь
            return {
                "id": answer_with_author.id,
                "body": answer_with_author.body,
                "created_at": answer_with_author.created_at,
                "updated_at": answer_with_author.updated_at,
                "author_id": answer_with_author.author_id,
                "question_id": answer_with_author.question_id,
                "is_accepted": answer_with_author.is_accepted,
                "votes_up": answer_with_author.votes_up,
                "votes_down": answer_with_author.votes_down,
                "author": {
                    "id": answer_with_author.author.id,
                    "username": answer_with_author.author.username,
                    "avatar_url": answer_with_author.author.avatar_url
                },
                "user_vote": user_vote
            }
        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            self._log_error(f"Ошибка при голосовании за ответ {answer_id}", e)
            raise 