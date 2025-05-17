#!/bin/bash

# Скрипт для запуска Celery воркеров

# Определяем корневую директорию проекта
PROJECT_ROOT=$(dirname "$(dirname "$0")")

# Переходим в корневую директорию
cd "$PROJECT_ROOT" || exit 1

# Количество воркеров (по умолчанию равно количеству ядер CPU)
WORKERS=${WORKERS:-$(nproc)}

# Очереди для обработки 
QUEUES=${QUEUES:-"default,email"}

# Запускаем Celery worker
celery -A app.tasks worker \
    --loglevel=INFO \
    --concurrency="$WORKERS" \
    --queues="$QUEUES" \
    --hostname=worker@%h \
    --autoscale="$WORKERS",3 \
    --max-tasks-per-child=1000

exit 0 