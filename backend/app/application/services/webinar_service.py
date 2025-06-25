# backend/app/application/services/webinar_service.py
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.application.services.base import BaseService, NotFoundError, ValidationError, AuthorizationError
from app.application.services.jitsi_service import JitsiService
from app.domain.models import Webinar, WebinarParticipant, User, Plant, WebinarStatus, ParticipantRole
from app.tasks.webinar_tasks import schedule_webinar_activation, cancel_webinar_activation
from app.domain.schemas.webinar import (
    WebinarCreate, WebinarUpdate, WebinarFilterParams,
    WebinarParticipantCreate, WebinarParticipantUpdate
)


class WebinarService(BaseService[Webinar]):
    """Сервис для работы с вебинарами"""
    
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.jitsi_service = JitsiService()
    
    async def create_webinar(
        self, 
        webinar_data: WebinarCreate, 
        host: User
    ) -> Webinar:
        """
        Создает новый вебинар
        
        Args:
            webinar_data: Данные для создания вебинара
            host: Пользователь-ведущий
            
        Returns:
            Созданный вебинар
        """
        # Проверяем права на создание вебинара
        if not (host.has_role("admin") or host.has_role("plant_expert")):
            raise AuthorizationError("Только администраторы и эксперты могут создавать вебинары")
        
        # Валидируем данные
        await self._validate_webinar_data(webinar_data)
        
        # Генерируем уникальное имя комнаты
        room_name = self.jitsi_service.generate_room_name(0, webinar_data.title)
        
        # Создаем вебинар
        webinar = Webinar(
            title=webinar_data.title,
            description=webinar_data.description,
            host_id=host.id,
            room_name=room_name,
            scheduled_at=webinar_data.scheduled_at,
            duration_minutes=webinar_data.duration_minutes,
            max_participants=webinar_data.max_participants,
            is_public=webinar_data.is_public,
            plant_topic_id=webinar_data.plant_topic_id,
            jitsi_room_config=webinar_data.jitsi_room_config,
            status=WebinarStatus.SCHEDULED
        )
        
        self.db.add(webinar)
        await self.db.commit()
        await self.db.refresh(webinar)
        
        # Обновляем имя комнаты с реальным ID
        webinar.room_name = self.jitsi_service.generate_room_name(webinar.id, webinar_data.title)
        await self.db.commit()
        
        # Добавляем ведущего как участника с ролью HOST
        await self.add_participant(webinar.id, host.id, ParticipantRole.HOST)

        # Планируем автоматическую активацию
        if webinar.scheduled_at:
            schedule_webinar_activation.delay(
                webinar.id,
                webinar.scheduled_at.isoformat()
            )
            self._log_info(f"Запланирована автоактивация вебинара {webinar.id} на {webinar.scheduled_at}")

        # Перезагружаем вебинар с полными данными
        created_webinar = await self.get_webinar(webinar.id)

        self._log_info(f"Created webinar {webinar.id} by user {host.id}")
        return created_webinar
    
    async def get_webinar(self, webinar_id: int) -> Webinar:
        """
        Получает вебинар по ID
        
        Args:
            webinar_id: ID вебинара
            
        Returns:
            Вебинар
        """
        query = select(Webinar).options(
            selectinload(Webinar.host),
            selectinload(Webinar.plant_topic),
            selectinload(Webinar.participants).selectinload(WebinarParticipant.user)
        ).where(Webinar.id == webinar_id)
        
        result = await self.db.execute(query)
        webinar = result.scalar_one_or_none()
        
        if not webinar:
            raise NotFoundError("Webinar", webinar_id)
        
        return webinar
    
    async def get_webinars(
        self, 
        filters: WebinarFilterParams,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Получает список вебинаров с фильтрацией и пагинацией
        
        Args:
            filters: Параметры фильтрации
            page: Номер страницы
            per_page: Количество элементов на странице
            
        Returns:
            Dict с вебинарами и метаданными пагинации
        """
        query = select(Webinar).options(
            selectinload(Webinar.host),
            selectinload(Webinar.plant_topic),
            selectinload(Webinar.participants).selectinload(WebinarParticipant.user)
        )
        
        # Применяем фильтры
        conditions = []
        
        if filters.title:
            conditions.append(Webinar.title.ilike(f"%{filters.title}%"))
        
        if filters.host_id:
            conditions.append(Webinar.host_id == filters.host_id)
        
        if filters.status:
            conditions.append(Webinar.status == filters.status)
        
        if filters.is_public is not None:
            conditions.append(Webinar.is_public == filters.is_public)
        
        if filters.plant_topic_id:
            conditions.append(Webinar.plant_topic_id == filters.plant_topic_id)
        
        if filters.date_from:
            conditions.append(Webinar.scheduled_at >= filters.date_from)
        
        if filters.date_to:
            conditions.append(Webinar.scheduled_at <= filters.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Сортировка по дате
        query = query.order_by(Webinar.scheduled_at.desc())
        
        # Подсчет общего количества
        count_query = select(func.count(Webinar.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await self.db.execute(count_query)
        total_items = total_result.scalar()
        
        # Пагинация
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await self.db.execute(query)
        webinars = result.scalars().all()
        
        total_pages = (total_items + per_page - 1) // per_page
        
        return {
            "items": webinars,
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
            "per_page": per_page
        }
    
    async def update_webinar(
        self, 
        webinar_id: int, 
        webinar_data: WebinarUpdate, 
        user: User
    ) -> Webinar:
        """
        Обновляет вебинар
        
        Args:
            webinar_id: ID вебинара
            webinar_data: Данные для обновления
            user: Пользователь, выполняющий обновление
            
        Returns:
            Обновленный вебинар
        """
        webinar = await self.get_webinar(webinar_id)
        
        # Проверяем права на редактирование
        if not (user.has_role("admin") or user.id == webinar.host_id):
            raise AuthorizationError("Только администраторы и ведущие могут редактировать вебинары")
        
        # Обновляем поля
        update_data = webinar_data.model_dump(exclude_unset=True)

        # Проверяем, изменилось ли время начала
        scheduled_at_changed = "scheduled_at" in update_data

        for field, value in update_data.items():
            setattr(webinar, field, value)

        # Если изменилось время начала, перепланируем активацию
        if scheduled_at_changed:
            # Отменяем старую задачу
            cancel_webinar_activation.delay(webinar_id)

            # Планируем новую, если есть новое время
            if webinar.scheduled_at:
                schedule_webinar_activation.delay(
                    webinar_id,
                    webinar.scheduled_at.isoformat()
                )
                self._log_info(f"Перепланирована автоактивация вебинара {webinar_id} на {webinar.scheduled_at}")

        await self.db.commit()
        await self.db.refresh(webinar)

        self._log_info(f"Updated webinar {webinar_id} by user {user.id}")
        return webinar
    
    async def delete_webinar(self, webinar_id: int, user: User) -> None:
        """
        Удаляет вебинар
        
        Args:
            webinar_id: ID вебинара
            user: Пользователь, выполняющий удаление
        """
        webinar = await self.get_webinar(webinar_id)
        
        # Проверяем права на удаление
        if not (user.has_role("admin") or user.id == webinar.host_id):
            raise AuthorizationError("Только администраторы и ведущие могут удалять вебинары")
        
        # Отменяем запланированную активацию
        cancel_webinar_activation.delay(webinar_id)

        await self.db.delete(webinar)
        await self.db.commit()

        self._log_info(f"Deleted webinar {webinar_id} by user {user.id}")
    
    async def add_participant(
        self, 
        webinar_id: int, 
        user_id: int, 
        role: ParticipantRole = ParticipantRole.PARTICIPANT
    ) -> WebinarParticipant:
        """
        Добавляет участника в вебинар
        
        Args:
            webinar_id: ID вебинара
            user_id: ID пользователя
            role: Роль участника
            
        Returns:
            Запись об участнике
        """
        # Проверяем, что участник еще не добавлен
        existing_query = select(WebinarParticipant).where(
            and_(
                WebinarParticipant.webinar_id == webinar_id,
                WebinarParticipant.user_id == user_id
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing_participant = existing_result.scalar_one_or_none()
        
        if existing_participant:
            return existing_participant
        
        # Создаем нового участника
        participant = WebinarParticipant(
            webinar_id=webinar_id,
            user_id=user_id,
            role=role
        )
        
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        
        return participant
    
    async def remove_participant(self, webinar_id: int, user_id: int) -> None:
        """
        Удаляет участника из вебинара
        
        Args:
            webinar_id: ID вебинара
            user_id: ID пользователя
        """
        query = select(WebinarParticipant).where(
            and_(
                WebinarParticipant.webinar_id == webinar_id,
                WebinarParticipant.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        participant = result.scalar_one_or_none()
        
        if participant:
            await self.db.delete(participant)
            await self.db.commit()
    
    async def join_webinar(self, webinar_id: int, user: User) -> Dict[str, Any]:
        """
        Присоединяет пользователя к вебинару и возвращает данные для подключения

        Args:
            webinar_id: ID вебинара
            user: Пользователь

        Returns:
            Данные для подключения к Jitsi
        """
        webinar = await self.get_webinar(webinar_id)

        # Проверяем статус вебинара - можно подключиться только к активным вебинарам
        if webinar.status != WebinarStatus.LIVE:
            status_messages = {
                WebinarStatus.SCHEDULED: "Вебинар еще не начался",
                WebinarStatus.ENDED: "Вебинар уже завершен",
                WebinarStatus.CANCELLED: "Вебинар отменен"
            }
            message = status_messages.get(webinar.status, f"Невозможно подключиться к вебинару со статусом {webinar.status.value}")

            return {
                "can_join": False,
                "message": message,
                "status": webinar.status.value,
                "jwt_token": None,
                "jitsi_url": None,
                "expires_at": None,
                "config": None
            }

        # Проверяем доступность вебинара
        if not webinar.is_public and user.id != webinar.host_id:
            # Проверяем, что пользователь приглашен
            participant_query = select(WebinarParticipant).where(
                and_(
                    WebinarParticipant.webinar_id == webinar_id,
                    WebinarParticipant.user_id == user.id
                )
            )
            participant_result = await self.db.execute(participant_query)
            participant = participant_result.scalar_one_or_none()
            
            if not participant:
                raise AuthorizationError("Вебинар приватный, требуется приглашение")
        
        # Добавляем пользователя как участника, если его еще нет
        await self.add_participant(webinar_id, user.id)
        
        # Обновляем время присоединения
        participant_query = select(WebinarParticipant).where(
            and_(
                WebinarParticipant.webinar_id == webinar_id,
                WebinarParticipant.user_id == user.id
            )
        )
        participant_result = await self.db.execute(participant_query)
        participant = participant_result.scalar_one()
        
        participant.joined_at = datetime.now(timezone.utc)
        await self.db.commit()
        
        # Генерируем JWT токен для Jitsi
        jwt_data = self.jitsi_service.generate_jwt_token(user, webinar)

        return {
            "can_join": True,
            "message": "Успешное подключение к вебинару",
            "status": webinar.status.value,
            "jwt_token": jwt_data["token"],
            "jitsi_url": jwt_data["jitsi_url"],
            "expires_at": jwt_data["expires_at"]
        }
    
    async def _validate_webinar_data(self, webinar_data: WebinarCreate) -> None:
        """
        Валидирует данные вебинара
        
        Args:
            webinar_data: Данные для валидации
        """
        # Проверяем дату
        # Если scheduled_at не имеет timezone, считаем его UTC
        scheduled_at = webinar_data.scheduled_at
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)

        if scheduled_at <= datetime.now(timezone.utc):
            raise ValidationError("Дата проведения должна быть в будущем")
        
        # Проверяем растение-тему, если указано
        if webinar_data.plant_topic_id:
            plant_query = select(Plant).where(Plant.id == webinar_data.plant_topic_id)
            plant_result = await self.db.execute(plant_query)
            plant = plant_result.scalar_one_or_none()
            
            if not plant:
                raise ValidationError(f"Растение с ID {webinar_data.plant_topic_id} не найдено")
