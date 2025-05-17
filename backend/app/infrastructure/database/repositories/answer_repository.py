from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.answer import Answer
from app.domain.models.vote import AnswerVote
from app.domain.models.question import Question
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError, DatabaseError

class AnswerRepository(BaseRepository[Answer]):
    """Репозиторий для работы с ответами на вопросы"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model_class=Answer)
    
    async def create_answer(self, question_id: int, body: str, author_id: int) -> Answer:
        """
        Создать новый ответ на вопрос
        
        Args:
            question_id: ID вопроса
            body: Текст ответа
            author_id: ID автора
            
        Returns:
            Answer: Созданный ответ
        """
        db_obj = Answer(
            body=body,
            question_id=question_id,
            author_id=author_id
        )
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj
    
    async def update_answer(self, db_obj: Answer, body: str) -> Answer:
        """
        Обновить текст ответа
        
        Args:
            db_obj: Объект ответа для обновления
            body: Новый текст ответа
            
        Returns:
            Answer: Обновленный ответ
        """
        db_obj.body = body
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj
    
    async def mark_as_accepted(self, answer_id: int, question_id: int) -> bool:
        """
        Отметить ответ как принятый
        
        Args:
            answer_id: ID ответа
            question_id: ID вопроса (для проверки)
            
        Returns:
            bool: True, если ответ успешно отмечен как принятый
        """
        try:
            # Сначала сбрасываем все принятые ответы для этого вопроса
            reset_stmt = (
                update(Answer)
                .where(Answer.question_id == question_id)
                .values(is_accepted=False)
            )
            await self.session.execute(reset_stmt)
            
            # Затем отмечаем нужный ответ как принятый
            stmt = (
                update(Answer)
                .where(
                    and_(
                        Answer.id == answer_id,
                        Answer.question_id == question_id
                    )
                )
                .values(is_accepted=True)
            )
            result = await self.session.execute(stmt)
            
            # Если ответ успешно отмечен, также отмечаем вопрос как решенный
            if result.rowcount > 0:
                question_stmt = (
                    update(Question)
                    .where(Question.id == question_id)
                    .values(is_solved=True)
                )
                await self.session.execute(question_stmt)
                return True
            
            return False
        except Exception as e:
            raise DatabaseError(f"Ошибка при отметке ответа как принятого: {str(e)}")
    
    async def get_for_question(self, question_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Получить все ответы для вопроса
        
        Args:
            question_id: ID вопроса
            user_id: ID текущего пользователя (для определения голоса)
            
        Returns:
            List[Dict[str, Any]]: Список ответов
        """
        try:
            from sqlalchemy.orm import joinedload
            
            stmt = (
                select(Answer)
                .options(joinedload(Answer.author))
                .where(Answer.question_id == question_id)
                .order_by(desc(Answer.is_accepted), desc(Answer.votes_up), Answer.created_at)
            )
            result = await self.session.execute(stmt)
            answers = result.scalars().all()
            
            # Преобразуем в список словарей
            answers_list = []
            for answer in answers:
                answer_dict = self._entity_to_dict(answer)
                
                # Добавляем информацию о голосе пользователя
                if user_id:
                    answer_dict["user_vote"] = await self._get_user_vote(answer.id, user_id)
                    
                answers_list.append(answer_dict)
                    
            return answers_list
        except Exception as e:
            raise DatabaseError(f"Ошибка при получении ответов для вопроса: {str(e)}")
    
    async def _get_user_vote(self, answer_id: int, user_id: int) -> Optional[str]:
        """
        Получить тип голоса пользователя за ответ
        
        Args:
            answer_id: ID ответа
            user_id: ID пользователя
            
        Returns:
            Optional[str]: Тип голоса или None, если пользователь не голосовал
        """
        stmt = select(AnswerVote).where(
            and_(
                AnswerVote.answer_id == answer_id,
                AnswerVote.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        vote = result.scalars().first()
        return vote.vote_type if vote else None
    
    def _entity_to_dict(self, entity) -> Dict[str, Any]:
        """
        Преобразовать модель SQLAlchemy в словарь
        
        Args:
            entity: Объект модели SQLAlchemy
            
        Returns:
            Dict[str, Any]: Словарь с данными
        """
        result = {}
        for column in entity.__table__.columns:
            result[column.name] = getattr(entity, column.name)
        
        # Обрабатываем отношения
        if hasattr(entity, "author") and entity.author:
            result["author"] = {
                "id": entity.author.id,
                "username": entity.author.username,
                "avatar_url": entity.author.avatar_url
            }
            
        return result 