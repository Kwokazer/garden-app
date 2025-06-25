# backend/app/application/services/jitsi_service.py
try:
    # Пытаемся импортировать PyJWT (правильная библиотека)
    import jwt
    # Проверяем, что это действительно PyJWT, а не старая jwt библиотека
    if not hasattr(jwt, 'encode'):
        raise ImportError("Wrong jwt library")
except (ImportError, AttributeError):
    # Если не получается, пробуем альтернативные способы
    try:
        from jose import jwt
    except ImportError:
        # В крайнем случае, используем python-jose
        import jose.jwt as jwt

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.application.services.base import BaseService, BusinessLogicError
from app.core.config import settings
from app.domain.models import User, Webinar, ParticipantRole


class JitsiService(BaseService):
    """Сервис для работы с Jitsi Meet JWT токенами"""
    
    def __init__(self):
        super().__init__()
        self.app_id = settings.JITSI_APP_ID
        self.app_secret = settings.JITSI_APP_SECRET
        self.jitsi_domain = settings.JITSI_DOMAIN
        
    def generate_jwt_token(
        self, 
        user: User, 
        webinar: Webinar, 
        expires_in_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Генерирует JWT токен для подключения к Jitsi Meet
        
        Args:
            user: Пользователь
            webinar: Вебинар
            expires_in_minutes: Время жизни токена в минутах
            
        Returns:
            Dict с токеном и метаданными
        """
        try:
            # Определяем роль пользователя в вебинаре
            is_moderator = self._is_user_moderator(user, webinar)
            
            # Время истечения токена
            exp_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
            # Генерируем уникальные идентификаторы для сессии
            session_id = str(uuid.uuid4())
            jwt_id = str(uuid.uuid4())

            # Payload для JWT токена
            payload = {
                "iss": self.app_id,  # Возвращаем оригинальный issuer
                "aud": "jitsi",  # Используем jitsi как audience
                "app_id": self.app_id,  # Добавляем app_id для Prosody
                "exp": int(exp_time.timestamp()),
                "iat": int(datetime.utcnow().timestamp()),
                "jti": jwt_id,  # Уникальный JWT ID
                "sub": f"user_{user.id}",  # Используем ID пользователя как subject
                "room": webinar.room_name,
                "moderator": is_moderator,  # Добавляем moderator на верхний уровень
                "admin": is_moderator,  # Добавляем admin на верхний уровень
                "affiliation": "owner" if is_moderator else "member",  # Добавляем affiliation на верхний уровень
                "context": {
                    "user": {
                        "id": str(user.id),
                        "name": user.username,
                        "email": user.email,
                        "avatar": user.avatar_url or "",
                        "moderator": is_moderator,
                        "admin": is_moderator,
                        "affiliation": "owner" if is_moderator else "member",  # Добавляем affiliation для правильного определения роли
                        "session_id": session_id,  # Уникальный идентификатор сессии
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)  # Уникальный timestamp в миллисекундах
                    },
                    "room": {
                        "name": webinar.room_name,
                        "isGuest": not is_moderator,  # Явно указываем, является ли пользователь гостем
                        "moderator": is_moderator  # Дублируем moderator в room контексте
                    },
                    "features": {
                        "livestreaming": is_moderator,
                        "recording": is_moderator,
                        "transcription": False,
                        "outbound-call": is_moderator
                    }
                }
            }

            # Добавляем дополнительные поля для более точного контроля ролей
            if not is_moderator:
                # Для обычных пользователей добавляем ограничения
                payload["context"]["features"]["screen-sharing"] = False
                payload["context"]["features"]["invite"] = False
                payload["context"]["features"]["kick-out"] = False
                payload["context"]["features"]["mute-others"] = False
            
            # Генерируем токен
            token = jwt.encode(payload, self.app_secret, algorithm="HS256")

            # Формируем URL для подключения к Jitsi серверу
            jitsi_url = f"{settings.JITSI_HTTP_URL}/{webinar.room_name}?jwt={token}"

            self._log_info(f"Generated JWT token for user {user.id} in webinar {webinar.id}, is_moderator: {is_moderator}, affiliation: {'owner' if is_moderator else 'member'}")
            self._log_debug(f"JWT payload: {payload}")
            
            return {
                "token": token,
                "room_name": webinar.room_name,
                "jitsi_url": jitsi_url,
                "expires_at": exp_time,
                "is_moderator": is_moderator
            }
            
        except Exception as e:
            self._log_error(f"Failed to generate JWT token for user {user.id}", e)
            raise BusinessLogicError(f"Не удалось создать токен для подключения: {str(e)}")
    

    
    def _is_user_moderator(self, user: User, webinar: Webinar) -> bool:
        """
        Проверяет, является ли пользователь модератором вебинара

        Args:
            user: Пользователь
            webinar: Вебинар

        Returns:
            True если пользователь модератор
        """
        # Ведущий всегда модератор (только если он admin или plant_expert)
        if user.id == webinar.host_id:
            if user.has_role("admin") or user.has_role("plant_expert"):
                self._log_info(f"User {user.id} is moderator: host with admin/plant_expert role")
                return True
            else:
                self._log_info(f"User {user.id} is host but not admin/plant_expert, not moderator")
                return False

        # Админы всегда модераторы
        if user.has_role("admin"):
            self._log_info(f"User {user.id} is moderator: has admin role")
            return True

        # Эксперты растений всегда модераторы
        if user.has_role("plant_expert"):
            self._log_info(f"User {user.id} is moderator: has plant_expert role")
            return True

        # Проверяем роль участника в вебинаре (только для admin и plant_expert)
        for participant in webinar.participants:
            if participant.user_id == user.id:
                if participant.role in [ParticipantRole.HOST, ParticipantRole.MODERATOR]:
                    if user.has_role("admin") or user.has_role("plant_expert"):
                        self._log_info(f"User {user.id} is moderator: participant role {participant.role} with admin/plant_expert")
                        return True
                    else:
                        self._log_info(f"User {user.id} has participant role {participant.role} but not admin/plant_expert, not moderator")
                        return False

        self._log_info(f"User {user.id} is not moderator: no qualifying conditions met")
        return False
    

    
    def validate_room_name(self, room_name: str) -> bool:
        """
        Валидирует имя комнаты Jitsi
        
        Args:
            room_name: Имя комнаты
            
        Returns:
            True если имя валидно
        """
        # Jitsi требует определенный формат имени комнаты
        if not room_name:
            return False
            
        # Только буквы, цифры, дефисы и подчеркивания
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, room_name))
    
    def generate_room_name(self, webinar_id: int, title: str) -> str:
        """
        Генерирует уникальное имя комнаты для вебинара
        
        Args:
            webinar_id: ID вебинара
            title: Название вебинара
            
        Returns:
            Уникальное имя комнаты
        """
        # Очищаем название от недопустимых символов
        import re
        clean_title = re.sub(r'[^a-zA-Z0-9_-]', '', title.replace(' ', '_'))
        clean_title = clean_title[:20]  # Ограничиваем длину
        
        # Добавляем ID и случайную строку для уникальности
        random_suffix = str(uuid.uuid4())[:8]
        room_name = f"webinar_{webinar_id}_{clean_title}_{random_suffix}"
        
        return room_name.lower()
