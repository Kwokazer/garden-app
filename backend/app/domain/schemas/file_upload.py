from typing import Dict, List, Optional, Any

from pydantic import Field

from app.domain.schemas.base import BaseSchema


class FileUploadResponse(BaseSchema):
    """Схема ответа при загрузке файла"""
    url: str = Field(..., description="URL загруженного файла")
    thumbnail_url: Optional[str] = Field(None, description="URL миниатюры")
    filename: str = Field(..., description="Оригинальное имя файла")
    size: int = Field(..., description="Размер файла в байтах")
    content_type: Optional[str] = Field(None, description="MIME тип файла")
    alt_text: Optional[str] = Field(None, description="Альтернативный текст")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    description: Optional[str] = Field(None, description="Описание изображения")


class FileValidationResponse(BaseSchema):
    """Схема ответа при валидации файла"""
    filename: str = Field(..., description="Имя файла")
    size: int = Field(..., description="Размер файла в байтах")
    content_type: Optional[str] = Field(None, description="MIME тип файла")
    valid: bool = Field(..., description="Валиден ли файл")
    image_info: Dict[str, Any] = Field(default_factory=dict, description="Информация об изображении")


class SupportedFormatsResponse(BaseSchema):
    """Схема ответа с информацией о поддерживаемых форматах"""
    allowed_extensions: List[str] = Field(..., description="Разрешенные расширения файлов")
    max_file_size_mb: int = Field(..., description="Максимальный размер файла в МБ")
    max_file_size_bytes: int = Field(..., description="Максимальный размер файла в байтах")
    supported_mime_types: List[str] = Field(..., description="Поддерживаемые MIME типы")


class PlantImageUploadRequest(BaseSchema):
    """Схема запроса для загрузки изображения растения"""
    alt_text: Optional[str] = Field(None, description="Альтернативный текст для изображения")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    description: Optional[str] = Field(None, description="Описание изображения")
    is_primary: bool = Field(False, description="Является ли изображение основным")


class PlantImageUploadResponse(BaseSchema):
    """Схема ответа при загрузке изображения растения"""
    id: int = Field(..., description="ID созданного изображения")
    plant_id: int = Field(..., description="ID растения")
    url: str = Field(..., description="URL изображения")
    thumbnail_url: Optional[str] = Field(None, description="URL миниатюры")
    alt: Optional[str] = Field(None, description="Альтернативный текст")
    title: Optional[str] = Field(None, description="Заголовок изображения")
    description: Optional[str] = Field(None, description="Описание изображения")
    is_primary: bool = Field(False, description="Является ли изображение основным")
    created_at: str = Field(..., description="Дата создания")
    updated_at: str = Field(..., description="Дата обновления")
