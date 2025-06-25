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
        """Создать вопрос"""
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
        """Обновить вопрос"""
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
        """Увеличить счетчик просмотров вопроса"""
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
        """Получить вопрос со всеми деталями, включая ответы, автора и связь с растением"""
        try:
            # Получаем вопрос с деталями
            stmt = (
                select(Question)
                .options(
                    joinedload(Question.author),
                    joinedload(Question.plant),
                    joinedload(Question.answers).joinedload(Answer.author).joinedload(User.roles)
                )
                .where(Question.id == question_id)
            )
            result = await self.session.execute(stmt)
            question = result.scalars().unique().first()  # unique() важно для joinedload
            
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
                    "avatar_url": getattr(question.author, "avatar_url", None)
                }
            else:
                # Fallback если автор не загружен
                question_dict["author"] = {
                    "id": question.author_id,
                    "username": "Неизвестно",
                    "avatar_url": None
                }
            
            # Добавляем информацию о растении
            if question.plant:
                question_dict["plant"] = {
                    "id": question.plant.id,
                    "name": question.plant.name,
                    "latin_name": getattr(question.plant, "latin_name", None),
                    "image_url": getattr(question.plant, "image_url", None)
                }
            # Если нет связи с растением, не добавляем поле plant
            
            # Получаем голоса пользователя за ответы (если есть ответы)
            answer_votes = {}
            if user_id and question.answers:
                answer_ids = [a.id for a in question.answers]
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
                votes_rows = votes_result.fetchall()
                for row in votes_rows:
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
                        # Получаем роли автора
                        author_roles = [role.name for role in answer.author.roles] if answer.author.roles else []

                        answer_dict["author"] = {
                            "id": answer.author.id,
                            "username": answer.author.username,
                            "avatar_url": getattr(answer.author, "avatar_url", None),
                            "roles": author_roles
                        }
                    else:
                        answer_dict["author"] = {
                            "id": answer.author_id,
                            "username": "Неизвестно",
                            "avatar_url": None,
                            "roles": []
                        }
                    
                    # Добавляем информацию о голосе пользователя за ответ
                    if user_id:
                        answer_dict["user_vote"] = answer_votes.get(answer.id)
                    else:
                        answer_dict["user_vote"] = None
                    
                    answers_list.append(answer_dict)
            
            question_dict["answers"] = answers_list
            question_dict["answers_count"] = len(answers_list)
            
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
                print(f"DEBUG: Question details {question_id}, user {user_id}, vote: {vote_type}")  # Debug лог
            else:
                question_dict["user_vote"] = None
            
            return question_dict
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при получении вопроса с деталями: {str(e)}\n{traceback.format_exc()}"
            raise DatabaseError(error_msg)
    
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
        """Получить список вопросов с фильтрацией, сортировкой и пагинацией"""
        try:
            print(f"DEBUG: get_many_with_details called with user_id={user_id}")
            
            # Основной запрос для вопросов
            query = select(Question)
            
            # Добавляем фильтры
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
            
            # Подсчет общего количества
            count_stmt = select(func.count()).select_from(query.alias())
            count_result = await self.session.execute(count_stmt)
            total = count_result.scalar_one()
            
            # Добавляем сортировку и пагинацию
            sort_column = getattr(Question, sort_by, Question.created_at)
            if sort_order.lower() == "asc":
                query = query.order_by(sort_column)
            else:
                query = query.order_by(desc(sort_column))
            
            query = query.offset(skip).limit(limit)
            
            # Получаем вопросы
            result = await self.session.execute(query)
            questions = result.scalars().all()
            print(f"DEBUG: Found {len(questions)} questions")
            
            if not questions:
                return [], total
            
            # Получаем связанные данные отдельными запросами
            question_ids = [q.id for q in questions]
            
            # 1. Авторы
            author_ids = list(set(q.author_id for q in questions))
            authors_result = await self.session.execute(
                select(User).where(User.id.in_(author_ids))
            )
            authors = {u.id: u for u in authors_result.scalars().all()}
            print(f"DEBUG: Loaded {len(authors)} authors")
            
            # 2. Растения
            plant_ids = list(set(q.plant_id for q in questions if q.plant_id))
            plants = {}
            if plant_ids:
                plants_result = await self.session.execute(
                    select(Plant).where(Plant.id.in_(plant_ids))
                )
                plants = {p.id: p for p in plants_result.scalars().all()}
                print(f"DEBUG: Loaded {len(plants)} plants")
            
            # 3. Количество ответов
            answers_count_result = await self.session.execute(
                select(Answer.question_id, func.count(Answer.id))
                .where(Answer.question_id.in_(question_ids))
                .group_by(Answer.question_id)
            )
            answers_count = {row[0]: row[1] for row in answers_count_result}
            
            # 4. Голоса пользователя (если авторизован)
            user_votes = {}
            if user_id:
                votes_result = await self.session.execute(
                    select(QuestionVote.question_id, QuestionVote.vote_type)
                    .where(
                        and_(
                            QuestionVote.question_id.in_(question_ids),
                            QuestionVote.user_id == user_id
                        )
                    )
                )
                user_votes = {row[0]: row[1] for row in votes_result}
                print(f"DEBUG: Found {len(user_votes)} votes for user {user_id}")
            
            # Собираем результат
            questions_list = []
            for question in questions:
                # Базовые поля
                question_dict = {column.name: getattr(question, column.name) for column in question.__table__.columns}
                
                # Автор (обязательно)
                author = authors.get(question.author_id)
                question_dict["author"] = {
                    "id": author.id if author else question.author_id,
                    "username": author.username if author else "Неизвестно",
                    "avatar_url": getattr(author, "avatar_url", None) if author else None
                }
                
                # Растение (опционально)
                if question.plant_id and question.plant_id in plants:
                    plant = plants[question.plant_id]
                    question_dict["plant"] = {
                        "id": plant.id,
                        "name": plant.name,
                        "latin_name": getattr(plant, "latin_name", None),
                        "image_url": getattr(plant, "image_url", None)
                    }
                
                # Мета-данные
                question_dict["answers_count"] = answers_count.get(question.id, 0)
                question_dict["user_vote"] = user_votes.get(question.id)
                
                questions_list.append(question_dict)
            
            print(f"DEBUG: Returning {len(questions_list)} questions")
            # Логируем первые 3 вопроса для проверки
            for i, q in enumerate(questions_list[:3]):
                author_info = f"author: {q['author']['username']}" if q.get('author') else "no author"
                plant_info = f"plant: {q['plant']['name']}" if q.get('plant') else "no plant"
                print(f"  Question {i}: {author_info}, {plant_info}")
            
            return questions_list, total
            
        except Exception as e:
            import traceback
            error_msg = f"Ошибка при получении списка вопросов: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_msg}")
            raise DatabaseError(error_msg)

    async def vote_for_question(self, question_id: int, user_id: int, vote_type: str) -> bool:
        """
        Проголосовать за вопрос
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            vote_type: Тип голоса (up/down)
            
        Returns:
            bool: True, если голос успешно обработан
        """
        try:
            print(f"DEBUG: vote_for_question called: question_id={question_id}, user_id={user_id}, vote_type={vote_type}")
            
            # Проверяем существующий голос
            existing_vote_stmt = select(QuestionVote).where(
                and_(
                    QuestionVote.question_id == question_id,
                    QuestionVote.user_id == user_id
                )
            )
            result = await self.session.execute(existing_vote_stmt)
            existing_vote = result.scalars().first()
            
            print(f"DEBUG: Existing vote: {existing_vote.vote_type if existing_vote else 'None'}")
            
            # Получаем вопрос
            question = await self.get(question_id)
            if not question:
                raise EntityNotFoundError("Question", question_id)
            
            print(f"DEBUG: Current question votes: up={question.votes_up}, down={question.votes_down}")
            
            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    # Удаляем голос (отмена)
                    await self.session.delete(existing_vote)
                    if vote_type == "up":
                        question.votes_up = max(0, question.votes_up - 1)
                    else:
                        question.votes_down = max(0, question.votes_down - 1)
                    print(f"DEBUG: Removed vote {vote_type}")
                else:
                    # Меняем тип голоса
                    existing_vote.vote_type = vote_type
                    if vote_type == "up":
                        question.votes_up += 1
                        question.votes_down = max(0, question.votes_down - 1)
                    else:
                        question.votes_down += 1
                        question.votes_up = max(0, question.votes_up - 1)
                    print(f"DEBUG: Changed vote from {('down' if vote_type == 'up' else 'up')} to {vote_type}")
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
                print(f"DEBUG: Added new vote {vote_type}")
            
            print(f"DEBUG: New question votes: up={question.votes_up}, down={question.votes_down}")
            
            # Сохраняем изменения в вопросе
            self.session.add(question)
            
            # Коммитим изменения
            await self.session.commit()
            print("DEBUG: Vote committed successfully")
            return True
            
        except Exception as e:
            print(f"DEBUG: Error in vote_for_question: {str(e)}")
            await self.session.rollback()
            raise DatabaseError(f"Ошибка при голосовании за вопрос: {str(e)}")

    async def _get_user_vote(self, question_id: int, user_id: int) -> Optional[str]:
        """Получить тип голоса пользователя за вопрос"""
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
        """Получить тип голоса пользователя за ответ"""
        stmt = select(AnswerVote).where(
            and_(
                AnswerVote.answer_id == answer_id,
                AnswerVote.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        vote = result.scalars().first()
        return vote.vote_type if vote else None