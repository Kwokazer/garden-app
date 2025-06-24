from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.common.security import check_permission
from app.application.services.file_upload_service import FileUploadService
from app.application.services.plant_service import PlantService
from app.core.constants import PERMISSION_MANAGE_PLANTS
from app.domain.schemas.file_upload import (
    FileUploadResponse, FileValidationResponse, PlantImageUploadResponse, SupportedFormatsResponse
)
from app.application.dependencies import get_plant_service

router = APIRouter()
security = HTTPBearer()


def get_file_upload_service() -> FileUploadService:
    """Dependency для получения сервиса загрузки файлов"""
    return FileUploadService()





@router.get("/supported-formats", response_model=SupportedFormatsResponse)
async def get_supported_formats(
    file_service: FileUploadService = Depends(get_file_upload_service)
) -> SupportedFormatsResponse:
    """
    Получить информацию о поддерживаемых форматах файлов
    """
    formats_info = file_service.get_supported_formats()
    return SupportedFormatsResponse(**formats_info)


@router.post("/validate", response_model=FileValidationResponse)
async def validate_file(
    file: UploadFile = File(..., description="Файл для валидации"),
    file_service: FileUploadService = Depends(get_file_upload_service)
) -> FileValidationResponse:
    """
    Валидировать файл без сохранения
    """
    file_info = await file_service.validate_and_get_file_info(file)
    return FileValidationResponse(**file_info)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="Загружаемый файл"),
    alt_text: Optional[str] = Form(None, description="Альтернативный текст"),
    title: Optional[str] = Form(None, description="Заголовок изображения"),
    description: Optional[str] = Form(None, description="Описание изображения"),
    file_service: FileUploadService = Depends(get_file_upload_service)
) -> FileUploadResponse:
    """
    Загрузить файл (временно без проверки прав для тестирования)
    """
    image_url, thumbnail_url, final_alt_text, metadata = await file_service.upload_plant_image(
        file=file,
        alt_text=alt_text,
        title=title,
        description=description
    )
    
    return FileUploadResponse(
        url=image_url,
        thumbnail_url=thumbnail_url,
        filename=metadata['original_filename'],
        size=metadata['file_size'],
        content_type=metadata['content_type'],
        alt_text=final_alt_text,
        title=title,
        description=description
    )


@router.post("/plants/{plant_id}/upload-image", response_model=PlantImageUploadResponse)
async def upload_plant_image(
    plant_id: int,
    file: UploadFile = File(..., description="Изображение растения"),
    alt_text: Optional[str] = Form(None, description="Альтернативный текст"),
    title: Optional[str] = Form(None, description="Заголовок изображения"),
    description: Optional[str] = Form(None, description="Описание изображения"),
    is_primary: bool = Form(False, description="Является ли изображение основным"),
    file_service: FileUploadService = Depends(get_file_upload_service),
    plant_service: PlantService = Depends(get_plant_service)
) -> PlantImageUploadResponse:
    """
    Загрузить изображение для конкретного растения (временно без проверки прав для тестирования)
    """
    try:
        # Проверяем, что растение существует
        plant = await plant_service.get_plant(plant_id)
        if not plant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Растение с ID {plant_id} не найдено"
            )
        
        # Загружаем и обрабатываем изображение
        image_url, thumbnail_url, final_alt_text, metadata = await file_service.upload_plant_image(
            file=file,
            alt_text=alt_text,
            title=title,
            description=description
        )
        
        # Создаем запись в базе данных
        from app.domain.schemas.plant_image import PlantImageCreate

        image_data = PlantImageCreate(
            plant_id=plant_id,
            url=image_url,
            alt=final_alt_text,
            title=title,
            description=description,
            thumbnail_url=thumbnail_url,
            is_primary=is_primary
        )
        
        # Добавляем изображение к растению
        created_image = await plant_service.add_plant_image(plant_id, image_data)
        
        return PlantImageUploadResponse(
            id=created_image.id,
            plant_id=plant_id,
            url=image_url,
            thumbnail_url=thumbnail_url,
            alt=final_alt_text,
            title=title,
            description=description,
            is_primary=is_primary,
            created_at=created_image.created_at.isoformat(),
            updated_at=created_image.updated_at.isoformat()
        )
        
    except HTTPException:
        # Если произошла ошибка после загрузки файла, удаляем его
        if 'image_url' in locals():
            file_service.delete_plant_image(image_url, thumbnail_url)
        raise
    except Exception as e:
        # Если произошла ошибка после загрузки файла, удаляем его
        if 'image_url' in locals():
            file_service.delete_plant_image(image_url, thumbnail_url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при создании изображения растения"
        )
