from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, func, desc, update, and_, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError

from app.domain.models.question import Question
from app.domain.models.tag import Tag
from app.domain.models.vote import QuestionVote, AnswerVote
from app.domain.models.answer import Answer
from app.domain.models.user import User
from app.domain.models.plant import Plant
from app.infrastructure.database.repositories.base import BaseRepository, EntityNotFoundError, DatabaseError

class QuestionRepository(BaseRepository[Question]):
    """Репозиторий для работы с вопросами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model_class=Question)

    async def create_question(self, obj_in: Dict[str, Any], author_id: int) -> Question:
        """
        Создать вопрос
        
        Args:
            obj_in: Данные вопроса
            author_id: ID автора
            
        Returns:
            Question: Созданный вопрос
        """
        try:
            db_obj = Question(
                title=obj_in["title"],
                body=obj_in["body"],
                author_id=author_id,
                plant_id=obj_in.get("plant_id")
            )
            self.session.add(db_obj)
            await self.session.flush()
            return db_obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Ошибка при создании вопроса: {str(e)}")

    async def update_question(self, db_obj: Question, obj_in: Dict[str, Any]) -> Question:
        """
        Обновить вопрос
        
        Args:
            db_obj: Объект вопроса для обновления
            obj_in: Новые данные
            
        Returns:
            Question: Обновленный вопрос
        """
        try:
            for field in ["title", "body", "is_solved", "plant_id"]:
                if field in obj_in and obj_in[field] is not None:
                    setattr(db_obj, field, obj_in[field])
            
            self.session.add(db_obj)
            await self.session.flush()
            return db_obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Ошибка при обновлении вопроса: {str(e)}")
    
    async def increment_view_count(self, question_id: int) -> bool:
        """
        Увеличить счетчик просмотров вопроса
        
        Args:
            question_id: ID вопроса
            
        Returns:
            bool: True, если счетчик успешно увеличен
        """
        try:
            stmt = (
                update(Question)
                .where(Question.id == question_id)
                .values(view_count=Question.view_count + 1)
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0
        except SQLAlchemyError as e:
            raise DatabaseError(f"Ошибка при увеличении счетчика просмотров: {str(e)}")
    
    async def get_with_details(self, question_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Получить вопрос со всеми деталями, включая ответы, автора и теги
        """
        try:
            # Получаем вопрос с деталями
            stmt = (
                select(Question)
                .options(
                    joinedload(Question.author),
                    joinedload(Question.plant),
                    joinedload(Question.answers).joinedload(Answer.author)
                )
                .where(Question.id == question_id)
            )
            result = await self.session.execute(stmt)
            question = result.scalars().first()
            
            if not question:
                return None
            
            # Преобразуем вопрос в словарь
            question_dict = {}
            
            # Базовые поля вопроса
            for column in question.__table__.columns:
                question_dict[column.name] = getattr(question, column.name)
            
            # Добавляем информацию об авторе
            if question.author:
                question_dict["author"] = {
                    "id": question.author.id,
                    "username": question.author.username,
                    "avatar_url": question.author.avatar_url if hasattr(question.author, "avatar_url") else None
                }
            
            # Добавляем информацию о растении
            if question.plant:
                question_dict["plant"] = {
                    "id": question.plant.id,
                    "name": question.plant.name,
                    "image_url": question.plant.image_url if hasattr(question.plant, "image_url") else None
                }
            
            # Предварительно загружаем голоса пользователя за ответы
            answer_votes = {}
            
            if user_id and question.answers:
                # Получаем ID всех ответов
                answer_ids = [a.id for a in question.answers]
                
                # Получаем все голоса пользователя за эти ответы
                votes_query = (
                    select(AnswerVote.answer_id, AnswerVote.vote_type)
                    .where(
                        and_(
                            AnswerVote.answer_id.in_(answer_ids),
                            AnswerVote.user_id == user_id
                        )
                    )
                )
                votes_result = await self.session.execute(votes_query)
                for row in votes_result:
                    answer_votes[row[0]] = row[1]  # answer_id -> vote_type
            
            # Добавляем ответы
            answers_list = []
            
            if question.answers:
                for answer in question.answers:
                    answer_dict = {}
                    
                    # Базовые поля ответа
                    for column in answer.__table__.columns:
                        answer_dict[column.name] = getattr(answer, column.name)
                    
                    # Добавляем информацию об авторе ответа
                    if answer.author:
                        answer_dict["author"] = {
                            "id": answer.author.id,
                            "username": answer.author.username,
                            "avatar_url": answer.author.avatar_url if hasattr(answer.author, "avatar_url") else None
                        }
                    
                    # Добавляем информацию о голосе пользователя
                    if user_id:
                        answer_dict["user_vote"] = answer_votes.get(answer.id)
                    
                    answers_list.append(answer_dict)
            
            question_dict["answers"] = answers_list
            
            # Добавляем информацию о голосе пользователя за вопрос
            if user_id:
                vote_query = (
                    select(QuestionVote.vote_type)
                    .where(
                        and_(
                            QuestionVote.question_id == question_id,
                            QuestionVote.user_id == user_id
                        )
                    )
                )
                vote_result = await self.session.execute(vote_query)
                vote_type = vote_result.scalar_one_or_none()
                question_dict["user_vote"] = vote_type
            
            return question_dict
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при получении вопроса с деталями: {str(e)}\n{traceback.format_exc()}"
            raise DatabaseError(error_msg)
    
    # Удаляем метод _entity_to_dict полностью и реализуем сериализацию напрямую в методах get_with_details и get_many_with_details

    async def get_many_with_details(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        plant_id: Optional[int] = None,
        author_id: Optional[int] = None,
        is_solved: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        user_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Получить список вопросов с фильтрацией, сортировкой и пагинацией
        """
        try:
            # Строим базовый запрос без joinedload для answers, так как они не нужны в списке
            query = (
                select(Question)
                .options(
                    joinedload(Question.author),
                    joinedload(Question.plant)
                )
            )
            
            # Добавляем условия фильтрации
            if search:
                query = query.where(
                    or_(
                        Question.title.ilike(f"%{search}%"),
                        Question.body.ilike(f"%{search}%")
                    )
                )

            if plant_id:
                query = query.where(Question.plant_id == plant_id)
            
            if author_id:
                query = query.where(Question.author_id == author_id)
            
            if is_solved is not None:
                query = query.where(Question.is_solved == is_solved)
            
            # Запрос для подсчета общего количества записей
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.session.execute(count_query)
            total = count_result.scalar_one()
            
            # Добавляем сортировку
            sort_column = getattr(Question, sort_by, Question.created_at)
            if sort_order.lower() == "asc":
                query = query.order_by(sort_column)
            else:
                query = query.order_by(desc(sort_column))
            
            # Добавляем пагинацию
            query = query.offset(skip).limit(limit)
            
            # Выполняем запрос
            result = await self.session.execute(query)
            questions = result.scalars().all()
            
            # Предварительно загружаем голоса пользователя
            user_votes = {}
            
            if user_id and questions:
                # Получаем ID всех вопросов
                question_ids = [q.id for q in questions]
                
                # Получаем все голоса пользователя за эти вопросы
                votes_query = (
                    select(QuestionVote.question_id, QuestionVote.vote_type)
                    .where(
                        and_(
                            QuestionVote.question_id.in_(question_ids),
                            QuestionVote.user_id == user_id
                        )
                    )
                )
                votes_result = await self.session.execute(votes_query)
                for row in votes_result:
                    user_votes[row[0]] = row[1]  # question_id -> vote_type
            
            # Получаем количество ответов для каждого вопроса
            answers_count = {}
            
            # Если есть вопросы, получаем количество ответов для них
            if questions:
                question_ids = [q.id for q in questions]
                answers_count_query = (
                    select(Answer.question_id, func.count(Answer.id))
                    .where(Answer.question_id.in_(question_ids))
                    .group_by(Answer.question_id)
                )
                answers_count_result = await self.session.execute(answers_count_query)
                for row in answers_count_result:
                    answers_count[row[0]] = row[1]  # question_id -> count
            
            # Теперь преобразуем вопросы в словари
            questions_list = []
            
            for question in questions:
                question_dict = {}
                
                # Базовые поля вопроса
                for column in question.__table__.columns:
                    question_dict[column.name] = getattr(question, column.name)
                
                # Добавляем информацию об авторе
                if question.author:
                    question_dict["author"] = {
                        "id": question.author.id,
                        "username": question.author.username,
                        "avatar_url": question.author.avatar_url if hasattr(question.author, "avatar_url") else None
                    }
                
                # Добавляем информацию о растении
                if question.plant:
                    question_dict["plant"] = {
                        "id": question.plant.id,
                        "name": question.plant.name,
                        "image_url": question.plant.image_url if hasattr(question.plant, "image_url") else None
                    }
                
                # Добавляем количество ответов из предварительно загруженного словаря
                question_dict["answers_count"] = answers_count.get(question.id, 0)
                
                # Добавляем информацию о голосе пользователя
                if user_id:
                    question_dict["user_vote"] = user_votes.get(question.id)
                
                questions_list.append(question_dict)
            
            return questions_list, total
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при получении списка вопросов: {str(e)}\n{traceback.format_exc()}"
            raise DatabaseError(error_msg)
    async def _get_user_vote(self, question_id: int, user_id: int) -> Optional[str]:
        """
        Получить тип голоса пользователя за вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            
        Returns:
            Optional[str]: Тип голоса или None, если пользователь не голосовал
        """
        stmt = select(QuestionVote).where(
            and_(
                QuestionVote.question_id == question_id,
                QuestionVote.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        vote = result.scalars().first()
        return vote.vote_type if vote else None
    
    async def _get_user_vote_for_answer(self, answer_id: int, user_id: int) -> Optional[str]:
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
        
        if hasattr(entity, "plant") and entity.plant:
            result["plant"] = {
                "id": entity.plant.id,
                "name": entity.plant.name,
                "image_url": entity.plant.image_url if hasattr(entity.plant, "image_url") else None
            }
        
        if hasattr(entity, "answers") and entity.answers:
            result["answers"] = [self._entity_to_dict(answer) for answer in entity.answers]
        
        return result 