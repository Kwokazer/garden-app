import logging
import sys
from typing import Optional
import datetime

from app.core.config import settings

class LoggerFactory:
    """
    Фабрика для создания и настройки логгеров
    """
    
    @staticmethod
    def create_logger(
        name: str, 
        level: Optional[int] = None,
        format_string: Optional[str] = None
    ) -> logging.Logger:
        """
        Создание и настройка логгера
        
        Args:
            name: Имя логгера
            level: Уровень логирования (если None, используется из настроек)
            format_string: Формат записей лога (если None, используется стандартный)
            
        Returns:
            logging.Logger: Настроенный логгер
        """
        # Получаем уровень логирования из настроек, если не указан
        if level is None:
            level = logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG
            
        # Устанавливаем формат логов
        if format_string is None:
            format_string = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
            
        # Создаем форматтер
        formatter = logging.Formatter(format_string)
        
        # Получаем или создаем логгер
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Сбрасываем все обработчики для повторной инициализации
        logger.handlers = []
        
        # Добавляем обработчик для вывода в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # В production режиме также добавляем запись в файл
        if settings.ENVIRONMENT == "production":
            # Создаем имя файла с текущей датой
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            file_handler = logging.FileHandler(f"logs/app_{current_date}.log")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        return logger

def get_logger(name: str) -> logging.Logger:
    """
    Получение настроенного логгера
    
    Args:
        name: Имя модуля или компонента для логгера
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    return LoggerFactory.create_logger(name) 