from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.answer import Answer
from app.domain.schemas.answer import (
    AnswerCreate, AnswerUpdate, AnswerDetailResponse
)
from app.domain.schemas.vote import AnswerVoteCreate as AnswerVoteSchema
from app.infrastructure.database.repositories import AnswerRepository, QuestionRepository, UserRepository
from app.infrastructure.cache.qa_cache import QACache

from .base import BaseService, NotFoundError, ValidationError, AuthorizationError

class AnswerService(BaseService):
    """Сервис для работы с ответами на вопросы"""
    
    def __init__(
        self,
        db: AsyncSession,
        qa_cache: Optional[QACache] = None
    ):
        super().__init__()
        self.db = db
        self.answer_repository = AnswerRepository(db)
        self.question_repository = QuestionRepository(db)
        self.qa_cache = qa_cache or QACache()
    
    async def create_answer(self, data: AnswerCreate, author_id: int) -> Dict[str, Any]:
        """
        Создать новый ответ
        
        Args:
            data: Данные ответа
            author_id: ID автора
            
        Returns:
            Dict[str, Any]: Созданный ответ
        """
        try:
            # Проверяем, существует ли вопрос
            question = await self.question_repository.get(data.question_id)
            if not question:
                raise NotFoundError("Question", data.question_id)
            
            # Создаем ответ
            answer = await self.answer_repository.create_answer(
                question_id=data.question_id,
                body=data.body,
                author_id=author_id
            )
            
            # Инвалидируем кеш вопроса
            await self.qa_cache.invalidate_question(data.question_id)
            
            # Получаем данные ответа для ответа API
            answers = await self.answer_repository.get_for_question(data.question_id, author_id)
            for answer_data in answers:
                if answer_data["id"] == answer.id:
                    return answer_data
            
            # Если не нашли ответ в списке (маловероятно), возвращаем базовую информацию
            return {
                "id": answer.id,
                "body": answer.body,
                "author_id": answer.author_id,
                "created_at": answer.created_at,
                "votes_up": answer.votes_up,
                "votes_down": answer.votes_down,
                "is_accepted": answer.is_accepted
            }
        except NotFoundError:
            raise
        except Exception as e:
            self._log_error("Ошибка при создании ответа", e)
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
            AuthorizationError: Если пользователь не имеет прав на обновление
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError("Answer", answer_id)
            
            # Проверяем права
            if answer.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise AuthorizationError("Редактирование ответа")
            
            # Обновляем ответ
            updated_answer = await self.answer_repository.update_answer(
                db_obj=answer,
                body=data.body
            )
            
            # Инвалидируем кеш вопроса
            await self.qa_cache.invalidate_question(answer.question_id)
            
            # Получаем данные ответа
            answers = await self.answer_repository.get_for_question(answer.question_id, user_id)
            for answer_data in answers:
                if answer_data["id"] == answer_id:
                    return answer_data
            
            # Если не нашли ответ в списке (маловероятно), возвращаем базовую информацию
            return {
                "id": updated_answer.id,
                "body": updated_answer.body,
                "author_id": updated_answer.author_id,
                "created_at": updated_answer.created_at,
                "votes_up": updated_answer.votes_up,
                "votes_down": updated_answer.votes_down,
                "is_accepted": updated_answer.is_accepted
            }
        except (NotFoundError, AuthorizationError):
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
            AuthorizationError: Если пользователь не имеет прав на удаление
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError("Answer", answer_id)
            
            # Проверяем права
            if answer.author_id != user_id:
                # TODO: Добавить проверку администратора
                raise AuthorizationError("Удаление ответа")
            
            # Сохраняем ID вопроса для инвалидации кеша
            question_id = answer.question_id
            
            # Удаляем ответ
            deleted = await self.answer_repository.delete(answer_id)
            
            # Инвалидируем кеш вопроса
            await self.qa_cache.invalidate_question(question_id)
            
            return deleted
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при удалении ответа {answer_id}", e)
            raise
    
    async def mark_answer_as_accepted(self, answer_id: int, user_id: int) -> Dict[str, Any]:
        """
        Отметить ответ как принятый
        
        Args:
            answer_id: ID ответа
            user_id: ID пользователя, который отмечает ответ
            
        Returns:
            Dict[str, Any]: Обновленный ответ
            
        Raises:
            NotFoundError: Если ответ не найден
            AuthorizationError: Если пользователь не имеет прав на принятие ответа
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError("Answer", answer_id)
            
            # Получаем вопрос
            question = await self.question_repository.get(answer.question_id)
            if not question:
                raise NotFoundError("Question", answer.question_id)
            
            # Проверяем, что пользователь является автором вопроса
            if question.author_id != user_id:
                raise AuthorizationError("Принятие ответа")
            
            # Отмечаем ответ как принятый
            success = await self.answer_repository.mark_as_accepted(answer_id, question.id)
            if not success:
                raise ValidationError("Не удалось отметить ответ как принятый")
            
            # Инвалидируем кеш вопроса
            await self.qa_cache.invalidate_question(question.id)
            await self.qa_cache.invalidate_questions_list()
            
            # Получаем обновленные данные ответа
            answers = await self.answer_repository.get_for_question(question.id, user_id)
            for answer_data in answers:
                if answer_data["id"] == answer_id:
                    return answer_data
            
            return {
                "id": answer.id,
                "is_accepted": True
            }
        except (NotFoundError, AuthorizationError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при отметке ответа {answer_id} как принятого", e)
            raise
    
    async def vote_for_answer(self, answer_id: int, vote_data: AnswerVoteSchema, user_id: int) -> Dict[str, Any]:
        """
        Проголосовать за ответ
        
        Args:
            answer_id: ID ответа
            vote_data: Данные голоса (up/down)
            user_id: ID пользователя, который голосует
            
        Returns:
            Dict[str, Any]: Обновленный ответ
            
        Raises:
            NotFoundError: Если ответ не найден
        """
        try:
            # Получаем ответ
            answer = await self.answer_repository.get(answer_id)
            if not answer:
                raise NotFoundError("Answer", answer_id)
            
            # Проверяем, не голосует ли пользователь за свой ответ
            if answer.author_id == user_id:
                raise ValidationError("Нельзя голосовать за свой собственный ответ")
            
            # Добавляем голос
            vote_type = vote_data.vote_type
            await self._handle_answer_vote(answer_id, user_id, vote_type)
            
            # Инвалидируем кеш вопроса
            await self.qa_cache.invalidate_question(answer.question_id)
            
            # Получаем обновленные данные ответа
            answers = await self.answer_repository.get_for_question(answer.question_id, user_id)
            for answer_data in answers:
                if answer_data["id"] == answer_id:
                    return answer_data
            
            return {
                "id": answer.id,
                "votes_up": answer.votes_up,
                "votes_down": answer.votes_down,
                "user_vote": vote_type if vote_type else None
            }
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self._log_error(f"Ошибка при голосовании за ответ {answer_id}", e)
            raise
    
    async def _handle_answer_vote(self, answer_id: int, user_id: int, vote_type: str) -> None:
        """
        Обработать голос за ответ
        
        Args:
            answer_id: ID ответа
            user_id: ID пользователя
            vote_type: Тип голоса (up/down)
        """
        # Получаем текущий голос пользователя
        current_vote = await self.answer_repository._get_user_vote(answer_id, user_id)
        
        # Если голос такой же, удаляем его (отмена голоса)
        if current_vote == vote_type:
            await self.db.execute(f"""
                DELETE FROM answer_votes
                WHERE answer_id = {answer_id} AND user_id = {user_id}
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_up = votes_up - 1
                    WHERE id = {answer_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_down = votes_down - 1
                    WHERE id = {answer_id}
                """)
        # Если голос противоположный, меняем его
        elif current_vote:
            await self.db.execute(f"""
                UPDATE answer_votes
                SET vote_type = '{vote_type}'
                WHERE answer_id = {answer_id} AND user_id = {user_id}
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_up = votes_up + 1, votes_down = votes_down - 1
                    WHERE id = {answer_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_up = votes_up - 1, votes_down = votes_down + 1
                    WHERE id = {answer_id}
                """)
        # Если голоса нет, добавляем новый
        else:
            await self.db.execute(f"""
                INSERT INTO answer_votes (answer_id, user_id, vote_type)
                VALUES ({answer_id}, {user_id}, '{vote_type}')
            """)
            
            # Обновляем счетчики
            if vote_type == "up":
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_up = votes_up + 1
                    WHERE id = {answer_id}
                """)
            else:
                await self.db.execute(f"""
                    UPDATE answers
                    SET votes_down = votes_down + 1
                    WHERE id = {answer_id}
                """) 