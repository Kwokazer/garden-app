import logging
from typing import Any, Dict, List, Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.application.services.base import (AuthenticationError,
                                           AuthorizationError,
                                           BusinessLogicError, NotFoundError,
                                           ServiceError)
from app.application.services.base import \
    ValidationError as ServiceValidationError

logger = logging.getLogger(__name__)

class ErrorResponse:
    """
    Стандартная структура ответа с ошибкой
    """
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать в словарь для ответа
        """
        response = {
            "status": "error",
            "message": self.message,
        }
        
        if self.error_code:
            response["error_code"] = self.error_code
            
        if self.details:
            response["details"] = self.details
            
        return response
    
    def to_response(self) -> JSONResponse:
        """
        Преобразовать в HTTP-ответ
        """
        return JSONResponse(
            status_code=self.status_code,
            content=self.to_dict()
        )


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """
    Обработчик ошибок сервисного слоя
    """
    logger.error(f"Ошибка сервиса при запросе {request.url}: {str(exc)}")
    
    if isinstance(exc, NotFoundError):
        return ErrorResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            message=str(exc),
            error_code="RESOURCE_NOT_FOUND",
            details={"entity_type": exc.entity_type, "entity_id": exc.entity_id}
        ).to_response()
        
    elif isinstance(exc, ServiceValidationError):
        return ErrorResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(exc),
            error_code="VALIDATION_ERROR",
            details=exc.errors
        ).to_response()
        
    elif isinstance(exc, AuthenticationError):
        return ErrorResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=str(exc),
            error_code="AUTHENTICATION_ERROR"
        ).to_response()
        
    elif isinstance(exc, AuthorizationError):
        return ErrorResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            message=str(exc),
            error_code="AUTHORIZATION_ERROR",
            details={"required_permission": exc.required_permission} if hasattr(exc, "required_permission") else None
        ).to_response()
        
    elif isinstance(exc, BusinessLogicError):
        return ErrorResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=str(exc),
            error_code="BUSINESS_LOGIC_ERROR"
        ).to_response()
        
    # Обработка других типов ошибок
    return ErrorResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Внутренняя ошибка сервера",
        error_code="INTERNAL_SERVER_ERROR"
    ).to_response()


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обработчик ошибок валидации запроса
    """
    errors: List[Dict[str, Any]] = exc.errors()
    logger.warning(f"Ошибка валидации при запросе {request.url}: {errors}")
    
    # Преобразование ошибок в удобный для чтения формат
    user_friendly_errors = {}
    
    for error in errors:
        loc = ".".join([str(x) for x in error["loc"]])
        user_friendly_errors[loc] = error["msg"]
    
    return ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Ошибка валидации данных запроса",
        error_code="VALIDATION_ERROR",
        details={"errors": user_friendly_errors}
    ).to_response()


async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic моделей
    """
    errors = exc.errors()
    logger.warning(f"Ошибка валидации Pydantic при запросе {request.url}: {errors}")
    
    # Преобразование ошибок в удобный для чтения формат
    user_friendly_errors = {}
    
    for error in errors:
        loc = ".".join([str(x) for x in error["loc"]])
        user_friendly_errors[loc] = error["msg"]
    
    return ErrorResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Ошибка валидации данных",
        error_code="VALIDATION_ERROR",
        details={"errors": user_friendly_errors}
    ).to_response()


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик неперехваченных исключений
    """
    logger.error(f"Неперехваченное исключение при запросе {request.url}: {str(exc)}", exc_info=True)
    
    return ErrorResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Внутренняя ошибка сервера",
        error_code="INTERNAL_SERVER_ERROR"
    ).to_response()


def register_exception_handlers(app):
    """
    Регистрация обработчиков исключений в приложении FastAPI
    """
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from pydantic import ValidationError
    from starlette.exceptions import HTTPException
    
    app.add_exception_handler(ServiceError, service_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, http_exception_handler) 