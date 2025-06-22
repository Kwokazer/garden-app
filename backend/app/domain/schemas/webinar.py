# backend/app/domain/schemas/webinar.py
import enum
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import Field, field_validator

from app.domain.schemas.base import BaseSchema, IDSchema, TimestampedSchema
from app.domain.schemas.user import UserRef
from app.domain.schemas.plant import PlantRef

# Enum для статуса вебинара
class WebinarStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"

# Enum для роли участника
class ParticipantRoleEnum(str, enum.Enum):
    HOST = "HOST"
    MODERATOR = "MODERATOR"
    PARTICIPANT = "PARTICIPANT"

class WebinarBase(BaseSchema):
    """Базовые поля вебинара"""
    title: str = Field(..., min_length=1, max_length=200, description="Название вебинара")
    description: Optional[str] = Field(None, description="Описание вебинара")
    scheduled_at: datetime = Field(..., description="Дата и время проведения")
    duration_minutes: int = Field(60, ge=15, le=480, description="Длительность в минутах (15-480)")
    max_participants: Optional[int] = Field(None, ge=2, le=1000, description="Максимальное количество участников")
    is_public: bool = Field(True, description="Публичный ли вебинар")
    plant_topic_id: Optional[int] = Field(None, description="ID растения - темы вебинара")
    jitsi_room_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация Jitsi комнаты")

class WebinarCreate(WebinarBase):
    """Схема для создания вебинара"""
    pass

class WebinarUpdate(BaseSchema):
    """Схема для обновления вебинара"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Название вебинара")
    description: Optional[str] = Field(None, description="Описание вебинара")
    scheduled_at: Optional[datetime] = Field(None, description="Дата и время проведения")
    duration_minutes: Optional[int] = Field(None, ge=15, le=480, description="Длительность в минутах")
    max_participants: Optional[int] = Field(None, ge=2, le=1000, description="Максимальное количество участников")
    is_public: Optional[bool] = Field(None, description="Публичный ли вебинар")
    status: Optional[WebinarStatusEnum] = Field(None, description="Статус вебинара")
    plant_topic_id: Optional[int] = Field(None, description="ID растения - темы вебинара")
    jitsi_room_config: Optional[Dict[str, Any]] = Field(None, description="Конфигурация Jitsi комнаты")

class WebinarParticipantRef(BaseSchema):
    """Краткая информация об участнике вебинара"""
    id: int = Field(..., description="ID записи участника")
    user: UserRef = Field(..., description="Информация о пользователе")
    role: ParticipantRoleEnum = Field(..., description="Роль участника")
    joined_at: Optional[datetime] = Field(None, description="Время присоединения")
    left_at: Optional[datetime] = Field(None, description="Время выхода")

class WebinarResponse(WebinarBase, IDSchema, TimestampedSchema):
    """Схема ответа для вебинара"""
    host_id: int = Field(..., description="ID ведущего")
    room_name: str = Field(..., description="Имя комнаты Jitsi")
    status: WebinarStatusEnum = Field(..., description="Статус вебинара")
    
    # Связанные данные
    host: UserRef = Field(..., description="Информация о ведущем")
    plant_topic: Optional["PlantRef"] = Field(None, description="Растение - тема вебинара")
    participants: List[WebinarParticipantRef] = Field(default_factory=list, description="Участники вебинара")
    
    # Вычисляемые поля
    participants_count: int = Field(0, description="Количество участников")
    
    @field_validator('participants_count', mode='before')
    @classmethod
    def calculate_participants_count(cls, v, info):
        if 'participants' in info.data:
            return len(info.data['participants'])
        return v

class WebinarListResponse(BaseSchema):
    """Схема ответа для списка вебинаров с пагинацией"""
    items: List[WebinarResponse] = Field(..., description="Список вебинаров")
    total_items: int = Field(..., description="Общее количество элементов")
    total_pages: int = Field(..., description="Общее количество страниц")
    page: int = Field(..., description="Текущая страница")
    per_page: int = Field(..., description="Количество элементов на странице")

class WebinarFilterParams(BaseSchema):
    """Параметры фильтрации вебинаров"""
    title: Optional[str] = Field(None, description="Поиск по названию (частичное совпадение)")
    host_id: Optional[int] = Field(None, description="Фильтр по ID ведущего")
    status: Optional[WebinarStatusEnum] = Field(None, description="Фильтр по статусу")
    is_public: Optional[bool] = Field(None, description="Фильтр по публичности")
    plant_topic_id: Optional[int] = Field(None, description="Фильтр по теме растения")
    date_from: Optional[datetime] = Field(None, description="Фильтр по дате начала")
    date_to: Optional[datetime] = Field(None, description="Фильтр по дате окончания")

# Схемы для участников
class WebinarParticipantCreate(BaseSchema):
    """Схема для добавления участника в вебинар"""
    user_id: int = Field(..., description="ID пользователя")
    role: ParticipantRoleEnum = Field(ParticipantRoleEnum.PARTICIPANT, description="Роль участника")

class WebinarParticipantUpdate(BaseSchema):
    """Схема для обновления участника вебинара"""
    role: Optional[ParticipantRoleEnum] = Field(None, description="Роль участника")

# Схемы для Jitsi интеграции
class JitsiTokenRequest(BaseSchema):
    """Запрос на получение JWT токена для Jitsi"""
    webinar_id: int = Field(..., description="ID вебинара")

class JitsiTokenResponse(BaseSchema):
    """Ответ с JWT токеном для Jitsi"""
    token: str = Field(..., description="JWT токен")
    room_name: str = Field(..., description="Имя комнаты")
    jitsi_url: str = Field(..., description="URL для подключения к Jitsi")
    expires_at: datetime = Field(..., description="Время истечения токена")

class JitsiConfigResponse(BaseSchema):
    """Конфигурация для встраивания Jitsi"""
    room_name: str = Field(..., description="Имя комнаты")
    domain: str = Field(..., description="Домен Jitsi")
    config_overwrite: Dict[str, Any] = Field(default_factory=dict, description="Переопределение конфигурации")
    interface_config_overwrite: Dict[str, Any] = Field(default_factory=dict, description="Переопределение интерфейса")
    user_info: Dict[str, Any] = Field(..., description="Информация о пользователе")
