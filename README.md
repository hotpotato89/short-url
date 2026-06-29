# Short URL (**MIT**)

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-28-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Alembic](https://img.shields.io/badge/Alembic-1.14-orange)
![QR Code](https://img.shields.io/badge/QR%20Code-Generated-brightgreen)
![Nginx](https://img.shields.io/badge/Nginx-1.27-green)
![Rate Limiting](https://img.shields.io/badge/Rate%20Limiting-SlowAPI-purple)
![TTL](https://img.shields.io/badge/TTL-Supported-blue)
![MIT](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)
![Deploy](https://img.shields.io/badge/Deploy-Render-46C3C4)

Сервис для сокращения ссылок с JWT-аутентификацией, ролями, кэшированием в Redis.

## 🌐 Демо

- **Фронтенд:** [short-url-ui-9240.onrender.com](https://short-url-ui-9240.onrender.com)
- **Swagger UI:** [short-url-8bjl.onrender.com/docs](https://short-url-8bjl.onrender.com/docs)

---

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
curl http://localhost/health
```

# Тестирование:

```bash
pytest
```

> Результат: **70+ зеленых тестов**.

## API эндпоинты

### 📱 QR-коды

Для каждой короткой ссылки можно сгенерировать QR-код.

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/url/{slug}/qr` | Получить QR-код в формате PNG |

**Особенности:**
 - Генерация на лету
 - Кэширование в Redis (24 часа)
 - Можно скачать с фронтенда
 - Не хранит бинарник в базе данных

### Авторизация

| Метод | Эндпоинт | Описание | Требует токен | only-admins |
|-------|----------|----------|---------------|-------------|
| POST | `/auth/register` | Регистрация | Нет | Нет |
| POST | `/auth/login` | Логин (access + refresh) | Нет | Нет |
| POST | `/auth/refresh` | Обновить access и refresh | Нет | Нет |
| POST | `/auth/logout` | Выход | Нет | Нет |
| GET | `/auth/me` | Профиль | Да | Нет |
| GET | `/auth/admin/users` | Все пользователи | Да | Да |
| PATCH | `/auth/admin/users/{user_id}/role` | Меняет роль пользователя | Да | Да |


### Ссылки

| Метод | Эндпоинт | Описание | Требует токен | only-admins |
|-------|----------|----------|---------------|-------------|
| POST | `/url` | Создать ссылку | Да | Нет |
| GET | `/url/my` | Список своих ссылок | Да | Нет |
| GET | `/url/{slug}` | Редирект | Нет | Нет |
| PUT | `/url/{slug}` | Изменить адрес (владелец) | Да | Нет |
| DELETE | `/url/{slug}` | Удалить (владелец) | Да | Нет |
| GET | `/url/admin/export` | Экспортировать все ссылки | Да| Да |

### Документация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI схема |

# Переменные окружение:
 - *в файле .env.example*

# Особенности:
 - JWT access (15 минут) + refresh (7 дней)
 - RSA подпись токенов (асимметричное шифрование)
 - **Argon2** хэширование паролей
 - Чистая архитектура (Service → Repository)
 - **Nginx** reverse proxy + раздача статики
 - Rate limiting (**SlowAPI**)
 - Кэширование редиректов в **Redis**
 - CI/CD через **Github Actions**
 - QR-коды через библиотеку **qrcode**
 - **TTL** система для ссылок


## 🧠 Как это работает

1. Пользователь регистрируется и получает JWT-токен.
2. Вставляет длинную ссылку → получает короткий `slug`.
3. При переходе по `/url/{slug}` происходит редирект.
4. Каждый переход учитывается в счётчике кликов.
5. Для любой ссылки можно сгенерировать QR-код.
6. Автор может менять `slug` и удалять его.



# Автор:
 - [hotpotato89](https://github.com/hotpotato89)