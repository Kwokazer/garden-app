import logging
from typing import Optional, Tuple

from fastapi import UploadFile, HTTPException, status

from app.application.services.image_processing_service import ImageProcessingService
from app.core.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE


class FileUploadService:
    """
    Сервис для загрузки и обработки файлов
    """
    
    def __init__(self):
        """
        Инициализация сервиса загрузки файлов
        """
        self.image_processor = ImageProcessingService()
        self.logger = logging.getLogger(__name__)
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Валидация загружаемого файла
        
        Args:
            file: Загружаемый файл
            
        Raises:
            HTTPException: Если файл не прошел валидацию
        """
        # Проверяем, что файл предоставлен
        if not file or not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не предоставлен"
            )
        
        # Проверяем размер файла
        if file.size and file.size > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Размер файла превышает максимально допустимый ({MAX_UPLOAD_SIZE // (1024*1024)} МБ)"
            )
        
        # Проверяем расширение файла
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Проверяем MIME тип
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
    
    async def upload_plant_image(
        self, 
        file: UploadFile,
        alt_text: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Tuple[str, str, Optional[str], dict]:
        """
        Загружает и обрабатывает изображение растения
        
        Args:
            file: Загружаемый файл
            alt_text: Альтернативный текст
            title: Заголовок изображения
            description: Описание изображения
            
        Returns:
            Tuple[str, str, Optional[str], dict]: (URL изображения, URL миниатюры, альт-текст, метаданные)
            
        Raises:
            HTTPException: При ошибке загрузки или обработки
        """
        try:
            # Валидируем файл
            self.validate_file(file)
            
            # Читаем содержимое файла
            file_content = await file.read()
            
            # Дополнительная валидация изображения
            if not self.image_processor.validate_image(file_content):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Файл не является валидным изображением"
                )
            
            # Получаем информацию об изображении
            image_info = self.image_processor.get_image_info(file_content)
            
            # Обрабатываем изображение
            image_path, image_url, thumbnail_path, thumbnail_url = self.image_processor.process_image(
                file_content, file.filename
            )
            
            # Формируем метаданные
            metadata = {
                'original_filename': file.filename,
                'file_size': len(file_content),
                'content_type': file.content_type,
                'image_info': image_info
            }
            
            # Используем предоставленный alt_text или генерируем из имени файла
            final_alt_text = alt_text or f"Изображение растения {file.filename}"
            
            self.logger.info(f"Успешно загружено изображение: {file.filename} -> {image_url}")
            
            return image_url, thumbnail_url, final_alt_text, metadata
            
        except HTTPException:
            # Перебрасываем HTTP исключения как есть
            raise
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке изображения {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера при обработке изображения"
            )
    
    def delete_plant_image(self, image_url: str, thumbnail_url: Optional[str] = None) -> bool:
        """
        Удаляет файлы изображения растения
        
        Args:
            image_url: URL основного изображения
            thumbnail_url: URL миниатюры
            
        Returns:
            bool: True если удаление прошло успешно
        """
        try:
            return self.image_processor.delete_image_files(image_url, thumbnail_url)
        except Exception as e:
            self.logger.error(f"Ошибка при удалении изображения {image_url}: {str(e)}")
            return False
    
    async def validate_and_get_file_info(self, file: UploadFile) -> dict:
        """
        Валидирует файл и возвращает информацию о нем без сохранения
        
        Args:
            file: Загружаемый файл
            
        Returns:
            dict: Информация о файле
            
        Raises:
            HTTPException: При ошибке валидации
        """
        try:
            # Валидируем файл
            self.validate_file(file)
            
            # Читаем содержимое файла
            file_content = await file.read()
            
            # Дополнительная валидация изображения
            if not self.image_processor.validate_image(file_content):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Файл не является валидным изображением"
                )
            
            # Получаем информацию об изображении
            image_info = self.image_processor.get_image_info(file_content)
            
            return {
                'filename': file.filename,
                'size': len(file_content),
                'content_type': file.content_type,
                'image_info': image_info,
                'valid': True
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Ошибка при валидации файла {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера при валидации файла"
            )
    
    def get_supported_formats(self) -> dict:
        """
        Возвращает информацию о поддерживаемых форматах
        
        Returns:
            dict: Информация о поддерживаемых форматах
        """
        return {
            'allowed_extensions': ALLOWED_IMAGE_EXTENSIONS,
            'max_file_size_mb': MAX_UPLOAD_SIZE // (1024 * 1024),
            'max_file_size_bytes': MAX_UPLOAD_SIZE,
            'supported_mime_types': [
                'image/jpeg',
                'image/png', 
                'image/webp',
                'image/gif'
            ]
        }
