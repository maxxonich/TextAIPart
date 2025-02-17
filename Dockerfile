FROM python:3.11-buster

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем пакеты
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем исходный код в контейнер
COPY . /app

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Запускаем приложение с помощью uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
