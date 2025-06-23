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
            
            # Payload для JWT токена
            payload = {
                "iss": self.app_id,
                "aud": "jitsi",
                "exp": int(exp_time.timestamp()),
                "iat": int(datetime.utcnow().timestamp()),
                "sub": "meet.jitsi",  # Базовый домен для JWT
                "room": webinar.room_name,
                "context": {
                    "user": {
                        "id": str(user.id),
                        "name": user.username,
                        "email": user.email,
                        "avatar": user.avatar_url or "",
                        "moderator": is_moderator
                    },
                    "features": {
                        "livestreaming": is_moderator,
                        "recording": is_moderator,
                        "transcription": False,
                        "outbound-call": is_moderator
                    }
                }
            }
            
            # Генерируем токен
            token = jwt.encode(payload, self.app_secret, algorithm="HS256")
            
            # Формируем URL для подключения к Jitsi серверу
            jitsi_url = f"{settings.JITSI_HTTP_URL}/{webinar.room_name}?jwt={token}"
            
            self._log_info(f"Generated JWT token for user {user.id} in webinar {webinar.id}")
            
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
    
    def get_jitsi_config(
        self, 
        user: User, 
        webinar: Webinar
    ) -> Dict[str, Any]:
        """
        Возвращает конфигурацию для встраивания Jitsi Meet
        
        Args:
            user: Пользователь
            webinar: Вебинар
            
        Returns:
            Dict с конфигурацией для iframe
        """
        try:
            is_moderator = self._is_user_moderator(user, webinar)
            
            # Базовая конфигурация
            config = {
                "room_name": webinar.room_name,
                "domain": self.jitsi_domain,
                "config_overwrite": {
                    "startWithAudioMuted": not is_moderator,
                    "startWithVideoMuted": not is_moderator,
                    "enableWelcomePage": False,
                    "enableUserRolesBasedOnToken": True,
                    "prejoinPageEnabled": False,
                    "requireDisplayName": True,
                    "disableDeepLinking": True,
                    "defaultLanguage": "ru",
                    "enableEmailInStats": False,
                    "enableDisplayNameInStats": False,
                    "enableClosePage": False,
                    "disableInviteFunctions": not is_moderator,
                    "doNotStoreRoom": True,
                    "disableRemoteMute": not is_moderator,
                    "disableModeratorIndicator": False,
                    "disableJoinLeaveSounds": False,
                    "enableLipSync": False,
                    "hideLobbyButton": not is_moderator,
                    "enableLobbyChat": False,
                    "enableInsecureRoomNameWarning": False,
                    "enableAutomaticUrlCopy": False,
                    "liveStreamingEnabled": is_moderator,
                    "recordingEnabled": is_moderator,
                    "fileRecordingsEnabled": is_moderator,
                    "localRecording": {
                        "enabled": is_moderator,
                        "format": "flac"
                    }
                },
                "interface_config_overwrite": {
                    "TOOLBAR_BUTTONS": self._get_toolbar_buttons(is_moderator),
                    "SETTINGS_SECTIONS": ["devices", "language", "moderator", "profile"],
                    "SHOW_JITSI_WATERMARK": False,
                    "SHOW_WATERMARK_FOR_GUESTS": False,
                    "SHOW_BRAND_WATERMARK": False,
                    "BRAND_WATERMARK_LINK": "",
                    "SHOW_POWERED_BY": False,
                    "DISPLAY_WELCOME_PAGE_CONTENT": False,
                    "DISPLAY_WELCOME_PAGE_TOOLBAR_ADDITIONAL_CONTENT": False,
                    "APP_NAME": "Garden Webinar",
                    "NATIVE_APP_NAME": "Garden Webinar",
                    "PROVIDER_NAME": "Garden",
                    "LANG_DETECTION": False,
                    "CONNECTION_INDICATOR_AUTO_HIDE_ENABLED": True,
                    "CONNECTION_INDICATOR_AUTO_HIDE_TIMEOUT": 5000,
                    "CONNECTION_INDICATOR_DISABLED": False,
                    "VIDEO_LAYOUT_FIT": "both",
                    "FILM_STRIP_MAX_HEIGHT": 120,
                    "TILE_VIEW_MAX_COLUMNS": 5,
                    "VERTICAL_FILMSTRIP": True,
                    "CLOSE_PAGE_GUEST_HINT": False,
                    "RANDOM_AVATAR_URL_PREFIX": False,
                    "RANDOM_AVATAR_URL_SUFFIX": False,
                    "FILM_STRIP_ONLY": False,
                    "HIDE_INVITE_MORE_HEADER": not is_moderator
                },
                "user_info": {
                    "displayName": user.username,
                    "email": user.email
                }
            }
            
            # Применяем пользовательскую конфигурацию вебинара, если есть
            if webinar.jitsi_room_config:
                config["config_overwrite"].update(webinar.jitsi_room_config)
            
            return config
            
        except Exception as e:
            self._log_error(f"Failed to get Jitsi config for user {user.id}", e)
            raise BusinessLogicError(f"Не удалось получить конфигурацию: {str(e)}")
    
    def _is_user_moderator(self, user: User, webinar: Webinar) -> bool:
        """
        Проверяет, является ли пользователь модератором вебинара
        
        Args:
            user: Пользователь
            webinar: Вебинар
            
        Returns:
            True если пользователь модератор
        """
        # Ведущий всегда модератор
        if user.id == webinar.host_id:
            return True
            
        # Админы всегда модераторы
        if user.has_role("admin"):
            return True
            
        # Проверяем роль участника в вебинаре
        for participant in webinar.participants:
            if participant.user_id == user.id:
                return participant.role in [ParticipantRole.HOST, ParticipantRole.MODERATOR]
        
        return False
    
    def _get_toolbar_buttons(self, is_moderator: bool) -> list:
        """
        Возвращает список кнопок тулбара в зависимости от роли
        
        Args:
            is_moderator: Является ли пользователь модератором
            
        Returns:
            Список кнопок тулбара
        """
        base_buttons = [
            "microphone", "camera", "closedcaptions", "desktop", "fullscreen",
            "fodeviceselection", "hangup", "profile", "chat", "recording",
            "livestreaming", "etherpad", "sharedvideo", "settings", "raisehand",
            "videoquality", "filmstrip", "invite", "feedback", "stats", "shortcuts",
            "tileview", "videobackgroundblur", "download", "help", "mute-everyone",
            "security"
        ]
        
        if not is_moderator:
            # Убираем кнопки модератора для обычных участников
            moderator_buttons = [
                "recording", "livestreaming", "invite", "mute-everyone", "security"
            ]
            base_buttons = [btn for btn in base_buttons if btn not in moderator_buttons]
        
        return base_buttons
    
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
