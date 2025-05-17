from typing import Any, Dict, List, Optional, Type


class BaseAppException(Exception):
    """
    Базовое исключение приложения
    """
    def __init__(
        self, 
        message: str, 
        error_code: str = "ERROR", 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ConfigError(BaseAppException):
    """
    Ошибка конфигурации
    """
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details
        )


class DatabaseError(BaseAppException):
    """
    Ошибка базы данных
    """
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(BaseAppException):
    """
    Ошибка внешнего сервиса
    """
    def __init__(
        self, 
        message: str, 
        service_name: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class ValidationException(BaseAppException):
    """
    Ошибка валидации данных
    """
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationException(BaseAppException):
    """
    Ошибка аутентификации
    """
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(BaseAppException):
    """
    Ошибка авторизации
    """
    def __init__(
        self, 
        message: str, 
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundException(BaseAppException):
    """
    Ошибка - ресурс не найден
    """
    def __init__(
        self, 
        message: str, 
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        if entity_type:
            details["entity_type"] = entity_type
        if entity_id:
            details["entity_id"] = entity_id
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details
        )


class BusinessLogicException(BaseAppException):
    """
    Ошибка бизнес-логики
    """
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )
