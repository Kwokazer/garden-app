import os
import shutil
import logging
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime
import aiofiles
import aiofiles.os
from urllib.parse import quote

# Для S3 (опционально)
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

from app.core.config import Settings

logger = logging.getLogger(__name__)

class WebinarStorageService:
    """Сервис для управления хранилищем записей вебинаров"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.storage_config = settings.get_webinar_storage_config()
        self.storage_type = self.storage_config["type"]
        
        if self.storage_type == "s3" and not HAS_BOTO3:
            raise ImportError("boto3 required for S3 storage. Install with: pip install boto3")
            
        # Инициализация S3 клиента если нужно
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                region_name=self.storage_config["region"],
                aws_access_key_id=self.storage_config["access_key"],
                aws_secret_access_key=self.storage_config["secret_key"]
            )
            self.bucket_name = self.storage_config["bucket"]
    
    async def save_recording(self, recording_id: str, source_path: str) -> Dict[str, Any]:
        """
        Сохраняет запись вебинара в хранилище
        
        Args:
            recording_id: ID записи
            source_path: Путь к исходному файлу записи
            
        Returns:
            Dict[str, Any]: Информация о сохраненной записи
        """
        try:
            if self.storage_type == "local":
                return await self._save_recording_local(recording_id, source_path)
            elif self.storage_type == "s3":
                return await self._save_recording_s3(recording_id, source_path)
            else:
                raise ValueError(f"Неподдерживаемый тип хранилища: {self.storage_type}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении записи {recording_id}: {e}")
            raise
    
    async def _save_recording_local(self, recording_id: str, source_path: str) -> Dict[str, Any]:
        """Сохраняет запись в локальном хранилище"""
        recordings_dir = self.storage_config["recordings_path"]
        target_dir = os.path.join(recordings_dir, recording_id)
        
        # Создаем директорию для записи
        await aiofiles.os.makedirs(target_dir, exist_ok=True)
        
        # Перемещаем файл записи
        recording_file = os.path.join(source_path, "recording.mp4")
        target_file = os.path.join(target_dir, f"{recording_id}.mp4")
        
        if await aiofiles.os.path.exists(recording_file):
            shutil.move(recording_file, target_file)
            file_size = os.path.getsize(target_file)
        else:
            raise FileNotFoundError(f"Файл записи не найден: {recording_file}")
        
        # Копируем превью если есть
        thumbnail_source = os.path.join(source_path, "thumbnail.jpg")
        thumbnail_target = os.path.join(target_dir, f"{recording_id}_thumbnail.jpg")
        
        has_thumbnail = False
        if await aiofiles.os.path.exists(thumbnail_source):
            shutil.copy2(thumbnail_source, thumbnail_target)
            has_thumbnail = True
        
        # Копируем метаданные если есть
        metadata_source = os.path.join(source_path, "metadata.json")
        metadata_target = os.path.join(target_dir, "metadata.json")
        
        if await aiofiles.os.path.exists(metadata_source):
            shutil.copy2(metadata_source, metadata_target)
        
        return {
            "storage_type": "local",
            "recording_path": target_file,
            "thumbnail_path": thumbnail_target if has_thumbnail else None,
            "file_size": file_size,
            "url": f"/api/v1/webinars/recordings/{recording_id}/download",
            "thumbnail_url": f"/api/v1/webinars/recordings/{recording_id}/thumbnail" if has_thumbnail else None
        }
    
    async def _save_recording_s3(self, recording_id: str, source_path: str) -> Dict[str, Any]:
        """Сохраняет запись в S3"""
        recordings_prefix = self.storage_config["recordings_prefix"]
        thumbnails_prefix = self.storage_config["thumbnails_prefix"]
        
        # Загружаем файл записи
        recording_file = os.path.join(source_path, "recording.mp4")
        s3_recording_key = f"{recordings_prefix}{recording_id}.mp4"
        
        if not os.path.exists(recording_file):
            raise FileNotFoundError(f"Файл записи не найден: {recording_file}")
        
        # Загружаем основной файл
        await self._upload_file_to_s3(recording_file, s3_recording_key)
        file_size = os.path.getsize(recording_file)
        
        # Загружаем превью если есть
        thumbnail_file = os.path.join(source_path, "thumbnail.jpg")
        s3_thumbnail_key = f"{thumbnails_prefix}{recording_id}_thumbnail.jpg"
        has_thumbnail = False
        
        if os.path.exists(thumbnail_file):
            await self._upload_file_to_s3(thumbnail_file, s3_thumbnail_key)
            has_thumbnail = True
        
        return {
            "storage_type": "s3",
            "recording_path": s3_recording_key,
            "thumbnail_path": s3_thumbnail_key if has_thumbnail else None,
            "file_size": file_size,
            "url": self._generate_s3_url(s3_recording_key),
            "thumbnail_url": self._generate_s3_url(s3_thumbnail_key) if has_thumbnail else None
        }
    
    async def _upload_file_to_s3(self, local_path: str, s3_key: str):
        """Загружает файл в S3"""
        try:
            with open(local_path, 'rb') as f:
                self.s3_client.upload_fileobj(f, self.bucket_name, s3_key)
        except ClientError as e:
            logger.error(f"Ошибка загрузки файла в S3: {e}")
            raise
    
    def _generate_s3_url(self, s3_key: str) -> str:
        """Генерирует URL для доступа к файлу в S3"""
        return f"https://{self.bucket_name}.s3.{self.storage_config['region']}.amazonaws.com/{s3_key}"
    
    async def get_recording_url(self, recording_id: str, signed: bool = False, expires_in: int = 3600) -> Optional[str]:
        """
        Получает URL для доступа к записи
        
        Args:
            recording_id: ID записи
            signed: Создать подписанный URL (для S3)
            expires_in: Время действия подписанного URL в секундах
            
        Returns:
            Optional[str]: URL записи или None если не найдена
        """
        try:
            if self.storage_type == "local":
                # Проверяем существование файла
                recordings_dir = self.storage_config["recordings_path"]
                recording_path = os.path.join(recordings_dir, recording_id, f"{recording_id}.mp4")
                
                if await aiofiles.os.path.exists(recording_path):
                    return f"/api/v1/webinars/recordings/{recording_id}/download"
                else:
                    return None
                    
            elif self.storage_type == "s3":
                recordings_prefix = self.storage_config["recordings_prefix"]
                s3_key = f"{recordings_prefix}{recording_id}.mp4"
                
                if signed:
                    # Генерируем подписанный URL
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.bucket_name, 'Key': s3_key},
                        ExpiresIn=expires_in
                    )
                    return url
                else:
                    return self._generate_s3_url(s3_key)
        except Exception as e:
            logger.error(f"Ошибка при получении URL записи {recording_id}: {e}")
            return None
    
    async def get_thumbnail_url(self, recording_id: str, signed: bool = False, expires_in: int = 3600) -> Optional[str]:
        """
        Получает URL для доступа к превью записи
        
        Args:
            recording_id: ID записи
            signed: Создать подписанный URL (для S3)
            expires_in: Время действия подписанного URL в секундах
            
        Returns:
            Optional[str]: URL превью или None если не найдено
        """
        try:
            if self.storage_type == "local":
                recordings_dir = self.storage_config["recordings_path"]
                thumbnail_path = os.path.join(recordings_dir, recording_id, f"{recording_id}_thumbnail.jpg")
                
                if await aiofiles.os.path.exists(thumbnail_path):
                    return f"/api/v1/webinars/recordings/{recording_id}/thumbnail"
                else:
                    return None
                    
            elif self.storage_type == "s3":
                thumbnails_prefix = self.storage_config["thumbnails_prefix"]
                s3_key = f"{thumbnails_prefix}{recording_id}_thumbnail.jpg"
                
                if signed:
                    url = self.s3_client.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': self.bucket_name, 'Key': s3_key},
                        ExpiresIn=expires_in
                    )
                    return url
                else:
                    return self._generate_s3_url(s3_key)
        except Exception as e:
            logger.error(f"Ошибка при получении URL превью {recording_id}: {e}")
            return None
    
    async def delete_recording(self, recording_id: str) -> bool:
        """
        Удаляет запись из хранилища
        
        Args:
            recording_id: ID записи
            
        Returns:
            bool: True если успешно удалено
        """
        try:
            if self.storage_type == "local":
                recordings_dir = self.storage_config["recordings_path"]
                recording_dir = os.path.join(recordings_dir, recording_id)
                
                if await aiofiles.os.path.exists(recording_dir):
                    shutil.rmtree(recording_dir)
                    return True
                    
            elif self.storage_type == "s3":
                recordings_prefix = self.storage_config["recordings_prefix"]
                thumbnails_prefix = self.storage_config["thumbnails_prefix"]
                
                # Удаляем основной файл и превью
                objects_to_delete = [
                    {'Key': f"{recordings_prefix}{recording_id}.mp4"},
                    {'Key': f"{thumbnails_prefix}{recording_id}_thumbnail.jpg"}
                ]
                
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                return True
                
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении записи {recording_id}: {e}")
            return False
    
    async def get_recording_file(self, recording_id: str) -> Optional[BinaryIO]:
        """
        Получает файл записи для скачивания
        
        Args:
            recording_id: ID записи
            
        Returns:
            Optional[BinaryIO]: Файловый объект или None
        """
        try:
            if self.storage_type == "local":
                recordings_dir = self.storage_config["recordings_path"]
                recording_path = os.path.join(recordings_dir, recording_id, f"{recording_id}.mp4")
                
                if await aiofiles.os.path.exists(recording_path):
                    return open(recording_path, 'rb')
                else:
                    return None
                    
            elif self.storage_type == "s3":
                # Для S3 возвращаем подписанный URL вместо файла
                return await self.get_recording_url(recording_id, signed=True)
                
        except Exception as e:
            logger.error(f"Ошибка при получении файла записи {recording_id}: {e}")
            return None
    
    async def cleanup_old_recordings(self, days: int = 365):
        """
        Очищает старые записи согласно политике хранения
        
        Args:
            days: Количество дней для хранения записей
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        try:
            if self.storage_type == "local":
                recordings_dir = self.storage_config["recordings_path"]
                
                if await aiofiles.os.path.exists(recordings_dir):
                    for recording_id in await aiofiles.os.listdir(recordings_dir):
                        recording_path = os.path.join(recordings_dir, recording_id)
                        
                        if os.path.isdir(recording_path):
                            # Проверяем время создания директории
                            creation_time = os.path.getctime(recording_path)
                            
                            if creation_time < cutoff_date:
                                shutil.rmtree(recording_path)
                                deleted_count += 1
                                logger.info(f"Удалена старая запись: {recording_id}")
                                
            elif self.storage_type == "s3":
                # Для S3 нужна более сложная логика, пока пропускаем
                pass
                
            logger.info(f"Очистка завершена. Удалено записей: {deleted_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке старых записей: {e}")
            
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Получает статистику использования хранилища
        
        Returns:
            Dict[str, Any]: Статистика хранилища
        """
        try:
            if self.storage_type == "local":
                recordings_dir = self.storage_config["recordings_path"]
                total_size = 0
                recording_count = 0
                
                if await aiofiles.os.path.exists(recordings_dir):
                    for recording_id in await aiofiles.os.listdir(recordings_dir):
                        recording_path = os.path.join(recordings_dir, recording_id)
                        
                        if os.path.isdir(recording_path):
                            recording_count += 1
                            for file in os.listdir(recording_path):
                                file_path = os.path.join(recording_path, file)
                                if os.path.isfile(file_path):
                                    total_size += os.path.getsize(file_path)
                
                return {
                    "storage_type": "local",
                    "total_recordings": recording_count,
                    "total_size_bytes": total_size,
                    "total_size_gb": round(total_size / (1024**3), 2),
                    "available_space_gb": shutil.disk_usage(recordings_dir).free / (1024**3)
                }
                
            elif self.storage_type == "s3":
                # Для S3 можно получить статистику через CloudWatch или API
                return {
                    "storage_type": "s3",
                    "bucket": self.bucket_name,
                    "note": "Подробная статистика доступна через AWS CloudWatch"
                }
                
        except Exception as e:
            logger.error(f"Ошибка при получении статистики хранилища: {e}")
            return {"error": str(e)}