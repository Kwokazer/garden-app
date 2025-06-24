import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageOps
from PIL.ExifTags import TAGS

from app.core.config import settings


class ImageProcessingService:
    """
    Сервис для обработки изображений растений
    """
    
    def __init__(self):
        """
        Инициализация сервиса обработки изображений
        """
        self.thumbnail_size = settings.THUMBNAIL_SIZE
        self.max_image_size = settings.MAX_IMAGE_SIZE
        self.image_quality = settings.IMAGE_QUALITY
        self.allowed_formats = settings.ALLOWED_IMAGE_FORMATS
        
        # Создаем директории если их нет
        os.makedirs(settings.PLANT_IMAGES_FULL_PATH, exist_ok=True)
        os.makedirs(settings.PLANT_THUMBNAILS_FULL_PATH, exist_ok=True)
    
    def validate_image(self, image_data: bytes) -> bool:
        """
        Валидация изображения
        
        Args:
            image_data: Данные изображения в байтах
            
        Returns:
            bool: True если изображение валидно
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                # Проверяем формат
                if img.format not in self.allowed_formats:
                    return False
                
                # Проверяем размер файла (уже проверен в константах)
                # Проверяем разрешение
                if img.size[0] > 5000 or img.size[1] > 5000:
                    return False
                    
                return True
        except Exception:
            return False
    
    def _fix_image_orientation(self, image: Image.Image) -> Image.Image:
        """
        Исправляет ориентацию изображения на основе EXIF данных

        Args:
            image: PIL изображение

        Returns:
            Image.Image: Изображение с исправленной ориентацией
        """
        try:
            # Получаем EXIF данные
            exif = image._getexif()
            if exif is not None:
                # Ищем тег ориентации (274 - это код для Orientation)
                orientation_tag = None
                for tag, value in exif.items():
                    if TAGS.get(tag) == 'Orientation':
                        orientation_tag = value
                        break

                if orientation_tag:
                    if orientation_tag == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation_tag == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation_tag == 8:
                        image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            # Если нет EXIF данных или ошибка, возвращаем исходное изображение
            pass

        return image
    
    def _optimize_image(self, image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
        """
        Оптимизирует изображение: изменяет размер если нужно
        
        Args:
            image: PIL изображение
            max_size: Максимальный размер (ширина, высота)
            
        Returns:
            Image.Image: Оптимизированное изображение
        """
        # Исправляем ориентацию
        image = self._fix_image_orientation(image)
        
        # Изменяем размер если изображение больше максимального
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Конвертируем в RGB если нужно (для JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон для прозрачных изображений
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def create_thumbnail(self, image: Image.Image) -> Image.Image:
        """
        Создает миниатюру изображения
        
        Args:
            image: PIL изображение
            
        Returns:
            Image.Image: Миниатюра
        """
        # Создаем копию для миниатюры
        thumbnail = image.copy()
        
        # Используем ImageOps.fit для создания квадратной миниатюры с обрезкой
        thumbnail = ImageOps.fit(
            thumbnail, 
            self.thumbnail_size, 
            Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )
        
        return thumbnail
    
    def process_image(self, image_data: bytes, filename: str) -> Tuple[str, str, str, str]:
        """
        Обрабатывает изображение: создает оптимизированную версию и миниатюру
        
        Args:
            image_data: Данные изображения в байтах
            filename: Оригинальное имя файла
            
        Returns:
            Tuple[str, str, str, str]: (путь к изображению, URL изображения, путь к миниатюре, URL миниатюры)
        """
        # Генерируем уникальное имя файла
        file_extension = Path(filename).suffix.lower()
        if not file_extension:
            file_extension = '.jpg'
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Открываем изображение
        with Image.open(BytesIO(image_data)) as original_image:
            # Оптимизируем основное изображение
            optimized_image = self._optimize_image(original_image, self.max_image_size)
            
            # Создаем миниатюру
            thumbnail = self.create_thumbnail(optimized_image)
            
            # Пути для сохранения
            image_path = os.path.join(settings.PLANT_IMAGES_FULL_PATH, unique_filename)
            thumbnail_path = os.path.join(settings.PLANT_THUMBNAILS_FULL_PATH, unique_filename)
            
            # Сохраняем основное изображение
            optimized_image.save(
                image_path,
                format='JPEG',
                quality=self.image_quality,
                optimize=True
            )
            
            # Сохраняем миниатюру
            thumbnail.save(
                thumbnail_path,
                format='JPEG',
                quality=self.image_quality,
                optimize=True
            )
            
            # Формируем URL
            image_url = f"{settings.PLANT_IMAGES_URL_PREFIX}/{unique_filename}"
            thumbnail_url = f"{settings.PLANT_THUMBNAILS_URL_PREFIX}/{unique_filename}"
            
            return image_path, image_url, thumbnail_path, thumbnail_url
    
    def delete_image_files(self, image_url: str, thumbnail_url: Optional[str] = None) -> bool:
        """
        Удаляет файлы изображения и миниатюры
        
        Args:
            image_url: URL основного изображения
            thumbnail_url: URL миниатюры (опционально)
            
        Returns:
            bool: True если удаление прошло успешно
        """
        try:
            # Извлекаем имя файла из URL
            filename = os.path.basename(image_url)
            
            # Удаляем основное изображение
            image_path = os.path.join(settings.PLANT_IMAGES_FULL_PATH, filename)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # Удаляем миниатюру
            if thumbnail_url:
                thumbnail_filename = os.path.basename(thumbnail_url)
                thumbnail_path = os.path.join(settings.PLANT_THUMBNAILS_FULL_PATH, thumbnail_filename)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
            
            return True
        except Exception:
            return False
    
    def get_image_info(self, image_data: bytes) -> dict:
        """
        Получает информацию об изображении
        
        Args:
            image_data: Данные изображения в байтах
            
        Returns:
            dict: Информация об изображении
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.size[0],
                    'height': img.size[1]
                }
        except Exception:
            return {}
