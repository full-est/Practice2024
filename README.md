# Practice2024
Этот проект включает FastAPI приложение и Telegram-бота, которые взаимодействуют с базой данных PostgreSQL. Весь проект можно запустить с помощью Docker и Docker Compose.

## Требования

- Docker
- Docker Compose

## Установка и запуск

1. **Клонируйте репозиторий:**

    ```sh
    git clone https://github.com/yourusername/Practice2024v2.git
    cd Practice2024v2
    ```

2. **Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные окружения:**

    ```dotenv
    DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_NAME=postgres
    DB_HOST=db
    DB_PORT=5432
    TOKEN='your_telegram_token'
    ```

    Замените `your_telegram_bot_token` на токен вашего Telegram-бота, а `your_fastapi_url`

3. **Запустите Docker Compose:**

    ```sh
    docker-compose up --build
    ```

    Эта команда соберет образы Docker для каждого сервиса (бота, приложения и базы данных) и запустит их.

4. **Проверьте, что все сервисы запущены:**

    Docker Compose автоматически запустит все три сервиса:
    - FastAPI приложение будет доступно по адресу `http://localhost:8000`
    - Telegram-бот будет работать в фоновом режиме и взаимодействовать с FastAPI и базой данных
    - PostgreSQL база данных будет запущена и доступна на порту 5432
    - Примечание: если произошла ошибка и некоторые сервисы не запустились, используйте команду:
   
   ```sh
    docker-compose up
    ```

5. **Остановите сервисы:**

    Чтобы остановить все сервисы, нажмите `Ctrl+C` в терминале, где запущен Docker Compose, или используйте команду:

    ```sh
    docker-compose down
    ```

## Структура проекта

- `main.py` - Файл с FastAPI приложением
- `tg.py` - Файл с кодом Telegram-бота
- `db.py` - Файл с кодом базы данных.
- `docker-compose.yml` - Конфигурационный файл Docker Compose
- `requirements.txt` - Файлы с зависимостями для каждого сервиса
- `Dockerfile` - конфигурационный файл для создания Docker-образа.

## Полезные команды

- **Просмотр логов:**

    ```sh
    docker-compose logs -f
    ```

- **Пересборка образов:**

    ```sh
    docker-compose up --build
    ```