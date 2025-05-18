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
        
        Args:
            question_id: ID вопроса
            user_id: ID текущего пользователя (для определения голоса)
            
        Returns:
            Dict[str, Any]: Вопрос с деталями или None, если не найден
        """
        try:
            # Получаем вопрос с деталями
            stmt = (
                select(Question)
                .options(
                    joinedload(Question.author),
                    joinedload(Question.tags),
                    joinedload(Question.plant),
                    joinedload(Question.answers).joinedload(Answer.author)
                )
                .where(Question.id == question_id)
            )
            result = await self.session.execute(stmt)
            question = result.scalars().first()
            
            if not question:
                return None
            
            # Преобразуем в словарь
            question_dict = self._entity_to_dict(question)
            
            # Добавляем информацию о голосе пользователя
            if user_id:
                question_dict["user_vote"] = await self._get_user_vote(question_id, user_id)
                
                # Также добавляем информацию о голосах пользователя для каждого ответа
                for answer in question_dict["answers"]:
                    answer["user_vote"] = await self._get_user_vote_for_answer(answer["id"], user_id)
            
            return question_dict
        except SQLAlchemyError as e:
            raise DatabaseError(f"Ошибка при получении вопроса с деталями: {str(e)}")
    
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
            # Строим базовый запрос
            query = (
                select(Question)
                .options(
                    joinedload(Question.author),
                    joinedload(Question.tags),
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
            
            # Преобразуем в список словарей
            questions_list = []
            for question in questions:
                question_dict = self._entity_to_dict(question)
                
                # Добавляем количество ответов
                question_dict["answers_count"] = len(question.answers)
                
                # Удаляем полные ответы, так как они не нужны в списке
                if "answers" in question_dict:
                    del question_dict["answers"]
                
                # Добавляем информацию о голосе пользователя
                if user_id:
                    question_dict["user_vote"] = await self._get_user_vote(question.id, user_id)
                
                questions_list.append(question_dict)
            
            return questions_list, total
        except SQLAlchemyError as e:
            raise DatabaseError(f"Ошибка при получении списка вопросов: {str(e)}")
    
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