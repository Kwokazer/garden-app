# Garden App

Веб-приложение для садоводства с видеоконференциями, фоновыми задачами и системой уведомлений.

## Стек технологий

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, Celery
- **Frontend:** Vue 3, Vite, Pinia, Vue Router
- **Базы данных:** PostgreSQL 15, MongoDB, Redis
- **Инфраструктура:** Docker, Nginx, RabbitMQ, Jitsi Meet
- **Инструменты:** MailHog (перехват писем), Flower (мониторинг Celery)

## Предварительные требования

- [Docker](https://docs.docker.com/get-docker/) и Docker Compose v2

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Kwokazer/garden-app.git
cd garden-app
```

### 2. Настроить переменные окружения

Скопировать шаблон для backend:

```bash
cp backend/.env.example backend/.env
```

Создать `.env` для frontend:

```bash
echo "VITE_API_URL=http://localhost:8000" > frontend/.env
```

> При необходимости отредактируйте `backend/.env` — для локальной разработки значения по умолчанию подойдут. Рекомендуется заменить `JWT_SECRET_KEY` (сгенерировать: `openssl rand -hex 32`).

### 3. Запустить проект

```bash
docker compose up --build
```

Для запуска в фоновом режиме:

```bash
docker compose up -d --build
```

### 4. Применить миграции

```bash
docker compose exec api alembic upgrade head
```

### 5. Открыть приложение

| Сервис | URL | Описание |
|---|---|---|
| Frontend | http://localhost:3000 | Веб-интерфейс |
| API Docs | http://localhost:8000/docs | Swagger-документация |
| RabbitMQ | http://localhost:15672 | Панель управления (`guest` / `guest`) |
| MailHog | http://localhost:8025 | Перехваченные письма |
| Flower | http://localhost:5555 | Мониторинг Celery |

## Архитектура сервисов

| Сервис | Технология | Порт | Назначение |
|---|---|---|---|
| api | FastAPI | 8000 | REST API |
| frontend | Vue 3 + Vite | 3000 | SPA-клиент |
| db | PostgreSQL 15 | 5432 | Основная БД |
| mongo | MongoDB | 27017 | Документоориентированная БД |
| redis | Redis | 6379 | Кэш и брокер задач |
| rabbitmq | RabbitMQ | 5672 / 15672 | Очередь сообщений |
| mailhog | MailHog | 1025 / 8025 | Перехват email |
| nginx | Nginx | 80 / 443 | Реверс-прокси |
| celery-worker | Celery | — | Фоновые задачи |
| celery-beat | Celery Beat | — | Периодические задачи |
| flower | Flower | 5555 | Мониторинг задач |
| jitsi-web | Jitsi Meet | 9091 | Видеоконференции |
| prosody | Prosody XMPP | 5280 | XMPP-сервер |
| jicofo | Jicofo | — | Управление конференциями |
| jvb | JVB | 10001/udp | Видеомост |
| jibri | Jibri | — | Запись конференций |

## Полезные команды

```bash
# Логи конкретного сервиса
docker compose logs -f api
docker compose logs -f frontend

# Зайти в контейнер backend
docker compose exec api bash

# Создать новую миграцию
docker compose exec api alembic revision --autogenerate -m "описание"

# Запустить тесты
docker compose exec api pytest

# Остановить проект
docker compose down

# Остановить и удалить все данные
docker compose down -v
```

## Возможные проблемы

- **Порт занят** — если порты 5432, 80 или другие уже используются, измените маппинг в `docker-compose.yml`.
- **Jibri не запускается** — сервис требует привилегий `SYS_ADMIN` и `NET_ADMIN`. На некоторых системах нужен запуск Docker с расширенными правами.
- **Миграции падают** — убедитесь, что PostgreSQL полностью запущен (`docker compose logs db`), затем повторите команду.
