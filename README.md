# Short URL

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Docker](https://img.shields.io/badge/Docker-28-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Alembic](https://img.shields.io/badge/Alembic-1.14-orange)
![QR Code](https://img.shields.io/badge/QR%20Code-Generated-brightgreen)
[![logging](https://img.shields.io/badge/logging-structlog-FF6B6B?logo=python&logoColor=white)](https://www.structlog.org/)
![Celery](https://img.shields.io/badge/Celery-5.6-brightgreen)
![Celery Beat](https://img.shields.io/badge/Celery%20Beat-Scheduler-blue)
![SHA-256](https://img.shields.io/badge/Token%20Storage-SHA256-orange)
![Argon2](https://img.shields.io/badge/Argon2-Secure-purple)
![Rate Limiting](https://img.shields.io/badge/Rate%20Limiting-SlowAPI-purple)
![TTL](https://img.shields.io/badge/TTL-Supported-blue)
![MIT](https://img.shields.io/badge/License-MIT-yellow)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF)
![Deploy](https://img.shields.io/badge/Deploy-Render-46C3C4)
![uv](https://img.shields.io/badge/uv-0.6-blue)
![Pytest](https://img.shields.io/badge/Pytest-9.1-blue?logo=pytest)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas&logoColor=white)
![XlsxWriter](https://img.shields.io/badge/XlsxWriter-3.0-0077B5?logo=python&logoColor=white)
![Export Audit](https://img.shields.io/badge/Export%20Audit-Logs-blue)
[![Enums](https://img.shields.io/badge/Typing-Enums-4B8BBE?logo=python&logoColor=white)](https://docs.python.org/3/library/enum.html)
![JWT](https://img.shields.io/badge/JWT-RS256-000000?logo=jsonwebtokens&logoColor=white)
[![simple-redis-cache](https://img.shields.io/badge/simple--redis--cache-PyPI-3776AB?logo=pypi&logoColor=white)](https://pypi.org/project/simple-redis-cache/)
[![Async Argon2](https://img.shields.io/badge/Async%20Argon2-v1.1.0-6A0DAD?logo=python)](https://pypi.org/project/async-argon2/)
![Credits](https://img.shields.io/badge/Credits-5%20free-FFD700)
![Credits System](https://img.shields.io/badge/Credits-System-blue)

Сервис для сокращения ссылок с JWT-аутентификацией, ролями, кэшированием в Redis, а также Celery с Celery Beat.

## 🌐 Демо

⚠️ Сайт работает в ограниченном режиме: Celery воркер отключён из-за ограничений бесплатного тарифа Render. Клики не учитываются, просроченные ссылки не удаляются, а всё остальное работает.

- **Swagger UI:** [short-url-8bjl.onrender.com/docs](https://short-url-8bjl.onrender.com/docs)
- **Фронтенд:** [short-url-ui-9240.onrender.com](https://short-url-ui-9240.onrender.com)

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
curl http://localhost:8000/health
```

# Тестирование:

```bash
pytest --cov src.app --cov-report=term
```

> Результат: **111 зеленых тестов.**

## API эндпоинты

## 💰 Кредитная система

Каждый пользователь получает **5 кредитов** при регистрации.

- **Создание ссылки** — тратит 1 кредит
- **При 0 кредитах** — создание ссылки недоступно (ошибка 403)

**Эндпоинты:**
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/credits` | Получить баланс пользователя |


---

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

| Метод | Эндпоинт | Описание | Требует токен |
|-------|----------|----------|---------------|
| POST | `/auth/register` | Регистрация | Нет |
| POST | `/auth/login` | Логин (access + refresh) | Нет |
| POST | `/auth/refresh` | Обновить access и refresh | Да (refresh) |
| POST | `/auth/logout` | Выход | Да (refresh) |
| GET | `/auth/me` | Профиль | Да |
| GET | `/auth/admin/users` | Все пользователи (админ) | Да |
| PATCH | `/auth/admin/users/{user_id}/role` | Меняет роль пользователя (админ)| Да |


### Ссылки

| Метод | Эндпоинт | Описание | Требует токен |
|-------|----------|----------|---------------|
| POST | `/url` | Создать ссылку | Да |
| GET | `/url/my` | Список своих ссылок | Да |
| GET | `/url/{slug}` | Редирект | Нет |
| PUT | `/url/{slug}` | Изменить адрес (владелец) | Да |
| DELETE | `/url/{slug}` | Удалить (владелец) | Да |
| GET | `/url/admin/export` | Экспортировать все ссылки (админ) | Да |
| GET | `/url/{slug}/info` | Получить данные конкретной ссылки (владелец или админ) | Да |

### Документация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI схема |

# Переменные окружение:
 - *в файле .env.example*

# Особенности:
 - JWT access (15 минут) + refresh (7 дней) токены
 - RSA подпись токенов (асимметричное шифрование)
 - Обработка ошибок при расшифровке `JWT` токена
 - **Async Argon2** хэширование паролей *(своя библиотека [репозиторий](https://github.com/hotpotato89/async-argon2))*
 - **SHA-256** хэширование refresh токенов в базе данных
 - Чистая архитектура (Service → Repository)
 - ~~**Nginx** reverse proxy + раздача статики~~ Убрано по причине ненадобности.
 - Rate limiting (**SlowAPI**)
 - Кэширование редиректов в **Redis** *(своя библиотека [репозиторий](https://github.com/hotpotato89/simple-redis-cache))*
 - CI/CD через **Github Actions**
 - QR-коды через библиотеку **qrcode**
 - **TTL** система для ссылок
 - Увеличение счетчика кликов происходит в фоне через **Celery**
 - Автоматическое удаление истекших ссылок через **Celery Beat**
 - Структурированные логи через [`structlog`](https://www.structlog.org/) с возможностью настроить `JSON` формат
 - Типобезопасность через `Python Enums`

### 📊 Аудит экспорта

Каждый экспорт данных (CSV/JSON/XLSX) логируется:
- Кто экспортировал (администратор)
- Когда был выполнен экспорт
- В каком формате

Просмотр логов доступен только супер-админу через эндпоинт `/url/admin/export-logs`.


## 🧠 Как это работает

1. Пользователь регистрируется и получает JWT-токен.
2. Вставляет длинную ссылку → получает короткий `slug`.
3. При переходе по `/url/{slug}` происходит редирект.
4. Каждый переход учитывается в счётчике кликов.
5. Для любой ссылки можно сгенерировать QR-код.
6. Автор может менять `slug` и удалять его.

> Имеется счетчик кликов

## 📦 Собственные библиотеки в проекте

Этот проект использует две мои собственные библиотеки, опубликованные на PyPI:

- **[`simple-redis-cache`](https://pypi.org/project/simple-redis-cache/)** — инструмент для кэширования синхронных и асинхронных функций в Redis.
- **[`async-argon2`](https://pypi.org/project/async-argon2/)** — асинхронная обёртка для хэширования паролей Argon2, не блокирующая event loop.

Обе библиотеки имеют 100% покрытие тестами, полную документацию и доступны для установки через pip.



# Автор:
 - [hotpotato89](https://github.com/hotpotato89)

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле [LICENSE](LICENSE).