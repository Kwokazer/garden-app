"""
Утилиты для валидации полей в схемах данных
"""
import re
from typing import Optional


def validate_password_strength(password: str, 
                               min_length: int = 8, 
                               require_uppercase: bool = True,
                               require_special: bool = True, 
                               require_digit: bool = True) -> Optional[str]:
    """
    Проверяет силу пароля согласно заданным требованиям.
    
    Args:
        password: Пароль для проверки
        min_length: Минимальная длина пароля
        require_uppercase: Требовать наличия заглавных букв
        require_special: Требовать наличия специальных символов
        require_digit: Требовать наличия цифр
        
    Returns:
        Optional[str]: Сообщение об ошибке или None, если пароль валидный
    """
    if len(password) < min_length:
        return f'Пароль должен содержать не менее {min_length} символов'
    
    if require_digit and not any(char.isdigit() for char in password):
        return 'Пароль должен содержать хотя бы одну цифру'
        
    if require_uppercase and not any(char.isupper() for char in password):
        return 'Пароль должен содержать хотя бы одну заглавную букву'
        
    if require_special and not any(char in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for char in password):
        return 'Пароль должен содержать хотя бы один специальный символ'
    
    return None

def validate_username(username: str) -> Optional[str]:
    """
    Проверяет валидность имени пользователя.
    
    Args:
        username: Имя пользователя для проверки
        
    Returns:
        Optional[str]: Сообщение об ошибке или None, если имя пользователя валидно
    """
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return 'Имя пользователя должно содержать только буквы, цифры и символ подчеркивания'
    
    return None 