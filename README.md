# Short URL

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-28-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Alembic](https://img.shields.io/badge/Alembic-1.14-orange)
![Nginx](https://img.shields.io/badge/Nginx-1.27-green)
![Rate Limiting](https://img.shields.io/badge/Rate%20Limiting-SlowAPI-purple)
![MIT](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)
![Deploy](https://img.shields.io/badge/Deploy-Render-46C3C4)

Сервис для сокращения ссылок с JWT-аутентификацией, кэшированием в Redis и фронтендом сгенерированным через ИИ.

# Быстрый старт

## Клонирование:

```bash
git clone https://github.com/hotpotato89/short-url.git
cd short-url
```

## Виртуальное окружение:

```bash
uv sync --frozen
source .venv/bin/activate
```

## Настройка окружения:

```bash
cp .env.example .env
```

## Генерация RSA ключей:

```bash
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -pubout -out keys/public.pem
```

## Запуск:

```bash
docker compose up -d --build
```

## Проверка:

```bash
curl http://localhost/api/health
```

# Тестирование:

```bash
pytest
```

# API эндпоинты:

## Авторизация:

 - POST /auth/register - регистрация
 - POST /auth/login - логин (access + refresh)
 - POST /auth/refresh - обновить access и refresh
 - POST /auth/logout - выход
 - GET /auth/me - профиль

## Ссылки:

 - POST /url - создать (требует токен)
 - GET /url/my - список своих ссылок (требует токен)
 - GET /url/{slug} - редирект
 - PUT /url/{slug} - изменить адрес (владелец)
 - DELETE /url/{slug} - удалить (владелец)

## Документация:

 - /docs - Swagger UI
 - /openapi.json - OpenAPI схема

# Переменные окружение:
 - *в файле .env.example*

# Особенности:
 - JWT access (15 минут) + refresh (7 дней)
 - RSA подпись токенов (асимметричное шифрование)
 - Argon2 хэширование паролей
 - Чистая архитектура (Service → Repository)
 - Nginx reverse proxy + раздача статики
 - Rate limiting (SlowAPI)
 - Кэширование редиректов в Redis

# Автор:
 - [hotpotato89](https://github.com/hotpotato89)

# 📄 Лицензия

Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).