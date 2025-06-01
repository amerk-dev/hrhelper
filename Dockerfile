# Базовый образ Python
FROM python:3.12-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование файла зависимостей и установка зависимостей Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копирование всего остального кода проекта в рабочую директорию /app
# Это включает manage.py и папку hrhelper/ (с settings.py)
COPY . .
# Если хочешь быть более точным, можно так:
# COPY manage.py .
# COPY hrhelper/ ./hrhelper/
# Но COPY . . проще, если .dockerignore настроен правильно (см. ниже)

# Команда для запуска (но она будет переопределена в docker-compose.yml для разработки)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]