import logging
from typing import Any, Dict, Generic, List, Optional, TypeVar

# Типовая переменная для сервисов
T = TypeVar('T')

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Базовый класс для ошибок сервисного слоя"""
    pass

class NotFoundError(ServiceError):
    """Ошибка, когда объект не найден"""
    def __init__(self, entity_type: str, entity_id: Any):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} с ID {entity_id} не найден")

class ValidationError(ServiceError):
    """Ошибка валидации данных"""
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        self.errors = errors or {}
        super().__init__(message)

class AuthenticationError(ServiceError):
    """Ошибка аутентификации"""
    pass

class AuthorizationError(ServiceError):
    """Ошибка авторизации (отсутствие прав)"""
    def __init__(self, required_permission: str = ""):
        self.required_permission = required_permission
        message = "Недостаточно прав для выполнения операции"
        if required_permission:
            message += f" (требуется: {required_permission})"
        super().__init__(message)

class BusinessLogicError(ServiceError):
    """Ошибка бизнес-логики"""
    pass

class BaseService(Generic[T]):
    """Базовый сервис с общей функциональностью для всех сервисов"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _log_error(self, error_message: str, exc: Optional[Exception] = None) -> None:
        """Логирует ошибку с трассировкой, если предоставлено исключение"""
        if exc:
            self.logger.error(f"{error_message}: {str(exc)}", exc_info=True)
        else:
            self.logger.error(error_message)
    
    def _log_info(self, message: str) -> None:
        """Логирует информационное сообщение"""
        self.logger.info(message)
    
    def _log_debug(self, message: str) -> None:
        """Логирует отладочное сообщение"""
        self.logger.debug(message) 