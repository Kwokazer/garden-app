import jwt
import time
import logging
from typing import Dict, Any, Optional
import aiohttp

from app.core.config import Settings

logger = logging.getLogger(__name__)

class JitsiService:
    """Сервис для взаимодействия с Jitsi Meet API"""
    
    def __init__(self, settings: Settings):
        self.api_base_url = settings.JITSI_API_URL
        self.app_id = settings.JITSI_APP_ID
        self.app_secret = settings.JITSI_APP_SECRET
        self.domain = settings.JITSI_DOMAIN
        
    def generate_jwt_token(self, room_name: str, user_id: int, 
                            user_name: str, user_email: str = None, 
                            is_moderator: bool = False) -> str:
        """
        Генерирует JWT токен для аутентификации в Jitsi Meet
        
        Args:
            room_name: Имя комнаты (вебинара)
            user_id: ID пользователя
            user_name: Имя пользователя для отображения
            user_email: Email пользователя (опционально)
            is_moderator: Флаг модератора
            
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
            "context": {
                "user": {
                    "id": str(user_id),
                    "name": user_name,
                    "avatar": f"/api/users/{user_id}/avatar",
                    "email": user_email or "",
                    "moderator": is_moderator
                }
            }
        }
        
        # Добавляем права модератора отдельно для совместимости со всеми версиями Jitsi
        if is_moderator:
            payload["moderator"] = True
            
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
            "url": self.get_room_url(room_name, token)
        }
    
    async def check_room_exists(self, room_name: str) -> bool:
        """
        Проверяет существование комнаты на сервере Jitsi
        
        Args:
            room_name: Имя комнаты
            
        Returns:
            bool: True если комната существует, иначе False
        """
        url = f"{self.api_base_url}/about/room/{room_name}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
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
        Примечание: Для этого должен быть настроен REST API в Jicofo
        
        Args:
            room_name: Имя комнаты
            auth_token: Токен авторизации (опционально)
            
        Returns:
            Dict[str, Any]: Информация об участниках комнаты
        """
        url = f"{self.api_base_url}/about/room/{room_name}/participants"
        headers = {}
        
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    return {"participants": [], "error": f"Status: {response.status}"}
            except Exception as e:
                logger.error(f"Ошибка при получении участников комнаты Jitsi: {e}")
                return {"participants": [], "error": str(e)}