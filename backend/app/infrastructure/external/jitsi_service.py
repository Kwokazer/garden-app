import jwt
import time
import logging
from typing import Dict, Any, Optional
import aiohttp
import aiofiles
import os
from urllib.parse import urljoin

from app.core.config import Settings

logger = logging.getLogger(__name__)

class JitsiService:
    """Сервис для взаимодействия с Jitsi Meet API"""
    
    def __init__(self, settings: Settings):
        self.api_base_url = settings.JITSI_API_URL
        self.http_base_url = settings.JITSI_HTTP_URL
        self.app_id = settings.JITSI_APP_ID
        self.app_secret = settings.JITSI_APP_SECRET
        self.domain = settings.JITSI_DOMAIN
        self.recordings_path = settings.WEBINAR_RECORDINGS_FULL_PATH
        
    def generate_jwt_token(self, room_name: str, user_id: int, 
                            user_name: str, user_email: str = None, 
                            is_moderator: bool = False, is_recorder: bool = False) -> str:
        """
        Генерирует JWT токен для аутентификации в Jitsi Meet
        
        Args:
            room_name: Имя комнаты (вебинара)
            user_id: ID пользователя
            user_name: Имя пользователя для отображения
            user_email: Email пользователя (опционально)
            is_moderator: Флаг модератора
            is_recorder: Флаг для записи (Jibri)
            
        Returns:
            str: Подписанный JWT токен
        """
        now = int(time.time())
        # Время жизни токена - 24 часа
        expiry = now + 86400
        
        # Создаем полезную нагрузку для JWT
        payload = {
            "aud": self.app_id,  # Аудитория - наше приложение
            "iss": self.app_id,  # Издатель - наше приложение
            "sub": self.domain,  # Субъект - домен Jitsi
            "exp": expiry,       # Срок действия токена
            "room": room_name,   # Имя комнаты
            "iat": now,          # Время создания токена
            "context": {
                "user": {
                    "id": str(user_id),
                    "name": user_name,
                    "avatar": f"/api/users/{user_id}/avatar",
                    "email": user_email or "",
                    "moderator": is_moderator
                },
                "features": {
                    # Разрешения для пользователя
                    "livestreaming": is_moderator,
                    "recording": is_moderator or is_recorder,
                    "transcription": is_moderator,
                    "outbound-call": is_moderator
                }
            }
        }
        
        # Добавляем права модератора отдельно для совместимости
        if is_moderator:
            payload["moderator"] = True
            
        # Для Jibri добавляем специальные права
        if is_recorder:
            payload["jibri"] = True
            payload["context"]["user"]["hidden-from-recorder"] = False
            
        # Генерируем JWT токен с подписью
        token = jwt.encode(payload, self.app_secret, algorithm="HS256")
        
        # Для pyjwt версии <2.0 token будет bytes, для >=2.0 - строка
        if isinstance(token, bytes):
            token = token.decode("utf-8")
            
        return token
        
    def get_room_url(self, room_name: str, token: Optional[str] = None) -> str:
        """
        Формирует URL для доступа к комнате Jitsi
        
        Args:
            room_name: Имя комнаты
            token: JWT токен (опционально)
            
        Returns:
            str: URL для доступа к комнате
        """
        url = f"{self.api_base_url}/{room_name}"
        
        if token:
            url += f"?jwt={token}"
            
        return url
        
    def get_room_config(self, room_name: str, user_id: int, user_name: str, 
                        user_email: str = None, is_moderator: bool = False) -> Dict[str, Any]:
        """
        Возвращает конфигурацию для подключения к комнате Jitsi
        
        Args:
            room_name: Имя комнаты
            user_id: ID пользователя
            user_name: Имя пользователя
            user_email: Email пользователя (опционально)
            is_moderator: Флаг модератора
            
        Returns:
            Dict[str, Any]: Конфигурация для подключения
        """
        token = self.generate_jwt_token(
            room_name, user_id, user_name, user_email, is_moderator
        )
        
        return {
            "room": room_name,
            "domain": self.domain,
            "api_url": self.api_base_url,
            "jwt": token,
            "url": self.get_room_url(room_name, token),
            "config": {
                "startWithVideoMuted": not is_moderator,
                "startWithAudioMuted": not is_moderator,
                "enableRecording": is_moderator,
                "enableLiveStreaming": is_moderator,
                "toolbarButtons": [
                    "camera", "chat", "closedcaptions", "desktop", "download",
                    "embedmeeting", "etherpad", "feedback", "filmstrip",
                    "fullscreen", "hangup", "help", "invite", "livestreaming",
                    "microphone", "mute-everyone", "mute-video-everyone",
                    "participants-pane", "profile", "recording", "security",
                    "select-background", "settings", "shareaudio", "sharedvideo",
                    "shortcuts", "stats", "tileview", "toggle-camera", "videoquality"
                ] if is_moderator else [
                    "camera", "chat", "desktop", "hangup", "microphone", 
                    "participants-pane", "profile", "settings", "tileview"
                ]
            }
        }
    
    async def check_room_exists(self, room_name: str) -> bool:
        """
        Проверяет существование комнаты на сервере Jitsi
        
        Args:
            room_name: Имя комнаты
            
        Returns:
            bool: True если комната существует, иначе False
        """
        url = f"{self.http_base_url}/about/room/{room_name}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("exists", False)
                    return False
        except Exception as e:
            logger.error(f"Ошибка при проверке комнаты Jitsi: {e}")
            return False
                
    async def get_active_participants(self, room_name: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает список активных участников в комнате Jitsi
        
        Args:
            room_name: Имя комнаты
            auth_token: Токен авторизации (опционально)
            
        Returns:
            Dict[str, Any]: Информация об участниках комнаты
        """
        url = f"{self.http_base_url}/about/room/{room_name}/participants"
        headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, ssl=False) as response:
                    if response.status == 200:
                        return await response.json()
                    return {"participants": [], "error": f"Status: {response.status}"}
        except Exception as e:
            logger.error(f"Ошибка при получении участников комнаты Jitsi: {e}")
            return {"participants": [], "error": str(e)}
            
    async def start_recording(self, room_name: str, moderator_token: str) -> Dict[str, Any]:
        """
        Запускает запись вебинара через Jibri
        
        Args:
            room_name: Имя комнаты
            moderator_token: JWT токен модератора
            
        Returns:
            Dict[str, Any]: Результат запуска записи
        """
        url = f"{self.http_base_url}/jibri/api/v1.0/start"
        headers = {
            "Authorization": f"Bearer {moderator_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "sessionId": room_name,
            "recording": {
                "appData": {
                    "file_recording_metadata": {
                        "share": False
                    }
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, ssl=False) as response:
                    result = await response.json()
                    if response.status == 200:
                        logger.info(f"Запись комнаты {room_name} запущена успешно")
                        return {"success": True, "data": result}
                    else:
                        logger.error(f"Ошибка при запуске записи: {result}")
                        return {"success": False, "error": result}
        except Exception as e:
            logger.error(f"Ошибка при запуске записи комнаты {room_name}: {e}")
            return {"success": False, "error": str(e)}
            
    async def stop_recording(self, room_name: str, moderator_token: str) -> Dict[str, Any]:
        """
        Останавливает запись вебинара
        
        Args:
            room_name: Имя комнаты
            moderator_token: JWT токен модератора
            
        Returns:
            Dict[str, Any]: Результат остановки записи
        """
        url = f"{self.http_base_url}/jibri/api/v1.0/stop"
        headers = {
            "Authorization": f"Bearer {moderator_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "sessionId": room_name
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, ssl=False) as response:
                    result = await response.json()
                    if response.status == 200:
                        logger.info(f"Запись комнаты {room_name} остановлена успешно")
                        return {"success": True, "data": result}
                    else:
                        logger.error(f"Ошибка при остановке записи: {result}")
                        return {"success": False, "error": result}
        except Exception as e:
            logger.error(f"Ошибка при остановке записи комнаты {room_name}: {e}")
            return {"success": False, "error": str(e)}
            
    async def get_recording_status(self, room_name: str) -> Dict[str, Any]:
        """
        Получает статус записи комнаты
        
        Args:
            room_name: Имя комнаты
            
        Returns:
            Dict[str, Any]: Статус записи
        """
        url = f"{self.http_base_url}/jibri/api/v1.0/status"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, ssl=False) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Ищем статус для конкретной комнаты
                        for session_info in result.get("sessions", []):
                            if session_info.get("sessionId") == room_name:
                                return {"success": True, "status": session_info.get("status"), "data": session_info}
                        return {"success": True, "status": "not_recording", "data": None}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Ошибка при получении статуса записи комнаты {room_name}: {e}")
            return {"success": False, "error": str(e)}
            
    async def get_recording_info(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о записи по ID
        
        Args:
            recording_id: ID записи
            
        Returns:
            Optional[Dict[str, Any]]: Информация о записи или None если не найдена
        """
        try:
            # Проверяем в директории обработанных записей
            processed_path = os.path.join(self.recordings_path, "processed", recording_id)
            metadata_file = os.path.join(processed_path, "metadata.json")
            
            if os.path.exists(metadata_file):
                async with aiofiles.open(metadata_file, 'r') as f:
                    metadata = await f.read()
                    import json
                    return json.loads(metadata)
                    
            # Проверяем в директории неудачных записей
            failed_path = os.path.join(self.recordings_path, "failed", recording_id)
            error_file = os.path.join(failed_path, "error.log")
            
            if os.path.exists(error_file):
                async with aiofiles.open(error_file, 'r') as f:
                    error_info = await f.read()
                    return {
                        "recording_id": recording_id,
                        "status": "failed",
                        "error": error_info
                    }
                    
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении информации о записи {recording_id}: {e}")
            return None