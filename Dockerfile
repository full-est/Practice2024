FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & python tg.py"]