#!/usr/bin/env python
"""
Скрипт для управления миграциями базы данных.
Позволяет создавать и применять миграции Alembic из командной строки.

Примеры использования:
    python migrate.py upgrade - Применить все миграции
    python migrate.py upgrade head - Применить миграции до последней версии
    python migrate.py upgrade +1 - Применить одну следующую миграцию
    python migrate.py downgrade -1 - Откатить одну миграцию
    python migrate.py revision --autogenerate -m "Описание изменений" - Создать новую миграцию
    python migrate.py history - Показать историю миграций
    python migrate.py current - Показать текущую версию БД
"""

import os
import sys
import argparse
from subprocess import call
from pathlib import Path

# Получаем корневую директорию проекта
ROOT_DIR = Path(__file__).resolve().parent.parent


def setup_alembic_environment():
    """Настраивает переменные окружения для миграций в локальной среде."""
    # При необходимости можно переопределить переменные окружения для локальной разработки
    env_updates = {
        "POSTGRES_HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "POSTGRES_DB": os.environ.get("POSTGRES_DB", "garden"),
        "POSTGRES_USER": os.environ.get("POSTGRES_USER", "postgres"),
        "POSTGRES_PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
    }
    
    # Проверяем, используем ли мы Docker
    if env_updates["POSTGRES_HOST"] == "postgres":
        print("Используются Docker-переменные. Заменяем POSTGRES_HOST на localhost для локальной миграции.")
        env_updates["POSTGRES_HOST"] = "localhost"
    
    # Обновляем переменные окружения
    os.environ.update(env_updates)
    
    return env_updates


def run_alembic(args):
    """Запускает команду Alembic с переданными аргументами."""
    # Настраиваем окружение для миграций
    env_updates = setup_alembic_environment()
    
    # Выводим информацию о подключении
    print(f"Используется подключение к БД: postgresql://{env_updates['POSTGRES_USER']}:***@{env_updates['POSTGRES_HOST']}:{env_updates['POSTGRES_PORT']}/{env_updates['POSTGRES_DB']}")
    
    # Формируем команду для Alembic
    command = ["alembic"] + args
    
    # Выполняем команду
    return call(command, cwd=ROOT_DIR)


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Утилита для управления миграциями базы данных")
    parser.add_argument("command", nargs="+", help="Команда и аргументы для Alembic")
    
    args = parser.parse_args()
    
    # Запускаем Alembic с переданными аргументами
    exit_code = run_alembic(args.command)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 