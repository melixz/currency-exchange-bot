# Currency Exchange Bot

## Описание
Чат-бот для отображения актуального курса валют.

## Функциональные требования
- Получение актуальных курсов валют с сайта Центрального банка России.
- Обновление данных в Redis.
- Ответы на команды `/exchange` и `/rates`.

## Установка и запуск

### Локально
1. Создайте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/Mac
    venv\Scripts\activate  # Для Windows
    ```
2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
3. Создайте файл `.env` в корневой директории и добавьте следующие переменные:
    ```env
    TELEGRAM_API_TOKEN=your_telegram_api_token_here
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
    ```
4. Запустите Redis:
    ```bash
    redis-server
    ```
5. Запустите обновление курсов валют:
    ```bash
    python currency_service.py
    ```
6. Запустите бота:
    ```bash
    python bot.py
    ```

### Используя Docker
1. Создайте файл `.env` в корневой директории и добавьте следующие переменные:
    ```env
    TELEGRAM_API_TOKEN=your_telegram_api_token_here
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```
2. Соберите и запустите контейнеры:
    ```bash
    docker-compose up --build
    ```

## Использование
- Команда `/exchange USD RUB 10` отображает стоимость 10 долларов в рублях.
- Команда `/rates` отправляет актуальные курсы валют.
