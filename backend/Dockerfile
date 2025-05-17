FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Для продакшена - закомментировать при разработке
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]