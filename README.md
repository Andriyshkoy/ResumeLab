# ResumeLab — генератор и улучшатель резюме

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-worker-37814A.svg)](https://docs.celeryq.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-336791.svg)](https://www.postgresql.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-broker-FF6600.svg)](https://www.rabbitmq.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF.svg)](https://vitejs.dev/)
[![Nginx](https://img.shields.io/badge/Nginx-edge-009639.svg)](https://nginx.org/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)

Сервис для регистрации пользователей, создания резюме и постановки задач на «улучшение» текста резюме в фоне через Celery. В комплекте — backend на FastAPI + PostgreSQL, брокер RabbitMQ, worker Celery, фронтенд на React (Vite), выдача через Nginx и готовый docker-compose для прод‑запуска.

## Оглавление

- [Что умеет](#что-умеет)
- [Архитектура](#архитектура)
- [Сервисы в docker-compose](#сервисы-в-docker-compose)
- [Быстрый старт (Docker Compose)](#быстрый-старт-docker-compose)
- [Локальная разработка (без Docker)](#локальная-разработка-без-docker)
- [Переменные окружения](#переменные-окружения)
- [API: обзор и примеры](#api-обзор-и-примеры)
- [Как работает «улучшение»](#как-работает-улучшение)
- [Логи и наблюдаемость](#логи-и-наблюдаемость)
- [Тесты](#тесты)
- [Структура репозитория](#структура-репозитория)
- [Статус проекта](#статус-проекта)
- [FAQ и рекомендации](#faq-и-рекомендации)

## Что умеет

- Регистрация и логин: email + пароль, выдача JWT access‑токена.
- Резюме: создание, список, просмотр, редактирование, удаление (только для владельца).
- Улучшения резюме: постановка задачи в очередь, отслеживание статуса, применение результата к резюме.
- Асинхронная обработка: Celery‑таска эмулирует LLM (ожидание + «улучшенный» текст) с ретраями.
- Безопасность: JWT, CORS, ограничение скорости на уровне Nginx для API, безопасные заголовки.
- Трассировка: `X-Request-ID` в ответах и JSON‑логах; в логах есть `user_id`.

## Архитектура

```mermaid
flowchart LR
  user((Пользователь)) --> nginx[Nginx]
  nginx --> spa[(SPA)]
  nginx --> api[FastAPI]
  api --> db[(PostgreSQL)]
  api --> rmq[(RabbitMQ)]
  worker[Celery worker] --> rmq
  worker --> db
```

- Backend: FastAPI (`app/main.py`), асинхронный SQLAlchemy, UoW + репозитории, Pydantic‑схемы.
- БД: PostgreSQL (в тестах/локально можно SQLite). Миграции — Alembic.
- Очереди: Celery (`app/celery_app/worker.py`, `app/celery_app/tasks.py`).
- Frontend: React + Vite, Axios, хранение JWT в LocalStorage/SessionStorage.
- Nginx: раздача SPA и прокси `/api` → backend; security‑заголовки, gzip, rate‑limit.
- Compose: сборка/запуск всего стека.

## Сервисы в docker-compose

| Сервис    | Назначение                    | Порт(ы)           |
|-----------|-------------------------------|-------------------|
| frontend  | Сборка SPA (Vite builder)     | —                 |
| nginx     | Edge, статика + прокси API    | 80 → localhost    |
| api       | FastAPI приложение            | 8000 (внутренний) |
| worker    | Celery worker                 | —                 |
| flower    | Мониторинг Celery             | 5555 (внутренний) |
| db        | PostgreSQL                    | 5432 (внутренний) |
| rabbitmq  | RabbitMQ (management включён) | 5672/15672 внутр. |

> Примечание: Flower и RabbitMQ UI не проброшены наружу. При необходимости добавьте `ports:` в `infrastructure/docker-compose.yml`.

## Быстрый старт (Docker Compose)

1) Подготовьте `.env`

Скопируйте `.env.example` → `.env` в корне и при необходимости отредактируйте:

```env
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app
SYNC_DATABASE_URL=postgresql+psycopg://app:app@db:5432/app
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
JWT_SECRET=<сложный_секрет>
# ...остальные значения смотрите в .env.example
```

2) Соберите образы

```bash
docker compose -f infrastructure/docker-compose.yml build
```

Переменные `VITE_*` для фронтенда берутся из `.env` как build‑args. Если `VITE_API_BASE_URL` пуст, SPA использует same‑origin `/api` (через Nginx).

3) Запустите стек

```bash
docker compose -f infrastructure/docker-compose.yml up
```

4) Откройте

- Приложение (SPA): http://localhost/
- API (через прокси): http://localhost/api/v1/...
- Swagger UI: http://localhost/docs
- ReDoc: http://localhost/redoc

## Локальная разработка (без Docker)

### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env (можно использовать SQLite для скорости)
# DATABASE_URL=sqlite+aiosqlite:///./app.db
# SYNC_DATABASE_URL=sqlite:///./app.db
# JWT_SECRET=dev_secret

alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm i
echo 'VITE_API_BASE_URL=http://localhost:8000' > .env.local
npm run dev
```

## Переменные окружения

- `DATABASE_URL`: async‑драйвер (например, `postgresql+asyncpg://...` или `sqlite+aiosqlite:///...`).
- `SYNC_DATABASE_URL`: sync‑URL для Alembic (`psycopg`/`sqlite`).
- `JWT_SECRET`: секрет подписания JWT.
- `ACCESS_TOKEN_TTL`: TTL токена в секундах (по умолчанию 3600).
- `RABBITMQ_URL`: адрес брокера AMQP.
- `CORS_ORIGINS`: JSON‑массив разрешённых origin (для dev можно `["*"]`).
- `IMPROVEMENT_DEDUP_ENABLED`: защита от дублей задач для одинакового контента.
- `CELERY_TASK_ALWAYS_EAGER`: выполнять задачи синхронно (удобно для тестов/CI).
- `API_PREFIX`: базовый префикс API (по умолчанию `/api/v1`).
- `LOG_LEVEL`: уровень логирования (`INFO` по умолчанию).
- Frontend build‑args: `VITE_API_BASE_URL`, `VITE_AUTH_STORAGE`, `VITE_POLL_INTERVAL_MS`, `VITE_POLL_TIMEOUT_MS`.

Полный перечень и подсказки — в `.env.example`.

## API: обзор и примеры

Эндпоинты (авторизованные требуют заголовок `Authorization: Bearer <token>`):

```text
POST   /api/v1/auth/register           # регистрация { email, password }
POST   /api/v1/auth/login              # логин → { access_token, expires_in }

POST   /api/v1/resume                  # создать резюме { title, content }
GET    /api/v1/resume                  # список (limit/offset)
GET    /api/v1/resume/{id}             # получить одно
PUT    /api/v1/resume/{id}             # обновить
DELETE /api/v1/resume/{id}             # удалить

POST   /api/v1/resume/{id}/improve     # поставить улучшение в очередь
GET    /api/v1/resume/{id}/improvements# список улучшений
GET    /api/v1/improvements/{id}       # статус/детали улучшения

GET    /health                         # проверка живости
```

Примеры cURL:

```bash
# Регистрация
curl -X POST http://localhost/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Passw0rd!"}'

# Логин
export TOKEN=$(curl -s -X POST http://localhost/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Passw0rd!"}' | jq -r .access_token)

# Создание резюме
curl -X POST http://localhost/api/v1/resume \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Python Dev","content":"Опыт: FastAPI, Postgres"}'

# Улучшение
curl -X POST http://localhost/api/v1/resume/<resume_id>/improve \
  -H "Authorization: Bearer $TOKEN"

# Статус улучшения
curl http://localhost/api/v1/improvements/<improvement_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Как работает «улучшение»

1. Пользователь вызывает `POST /resume/{id}/improve`.
2. Создаётся запись `ResumeImprovement` со статусом `queued` и сохраняется исходный текст.
3. Celery‑воркер помечает `processing`, «эмулирует» LLM (задержка ~3с) и формирует новый текст.
4. По завершении:
   - сохраняется `new_content`, статус → `done`, `applied=true`;
   - контент исходного резюме перезаписывается новым.
5. При ошибках/ретраях статус обновляется; финальный фейл → `failed` c текстом ошибки.
6. Опция `IMPROVEMENT_DEDUP_ENABLED=true` блокирует дубль для того же контента.

## Логи и наблюдаемость

- JSON‑логи с полями: `ts`, `level`, `message`, `request_id`, `user_id`, `logger`.
- Корреляция:
  - передайте `X-Request-ID` во входящем запросе — он вернётся в ответе и попадёт в логи;
  - `user_id` добавляется в контекст после аутентификации.
- Flower поднимается во внутренней сети (без порта). Чтобы открыть снаружи — добавьте `ports:` к сервису `flower` в compose.

## Тесты

```bash
pytest -q
```

Тесты используют SQLite и `CELERY_TASK_ALWAYS_EAGER=true` для предсказуемости.

## Структура репозитория

- `app/main.py` — создание FastAPI‑приложения, маршруты, middleware.
- `app/api/routes/*` — ручки `auth`, `resume`, `improvements`, `health`.
- `app/models/*` — SQLAlchemy‑модели: `User`, `Resume`, `ResumeImprovement` + статусы.
- `app/repositories/*` — слой доступа к данным (UoW + репозитории).
- `app/celery_app/*` — Celery‑приложение и таски.
- `app/core/*` — настройки, security (JWT, пароли), конфиг.
- `infrastructure/*` — Dockerfiles, Nginx, `docker-compose.yml`.
- `frontend/*` — исходники SPA на React + Vite.

## Статус проекта

Сделано:

- Бэкенд: аутентификация, CRUD резюме, постановка и отслеживание улучшений, JSON‑логи, CORS.
- Воркер: Celery‑таска с ретраями и безопасной обработкой ошибок.
- Инфраструктура: Nginx с security‑заголовками и rate‑limit, docker‑compose для прод‑запуска.
- Фронтенд: заготовка SPA, Axios‑клиент с `Authorization` и `X-Request-ID`, форма резюме с Markdown‑превью.
- Тесты: базовый e2e‑тест CRUD резюме.

Планы:

- Реальный клиент LLM вместо заглушки (`app/celery_app/tasks.py`) и конфигурация провайдера.
- Полноценные страницы SPA: листинг/детали резюме, очередь улучшений, аутентификация, уведомления.
- Доп. безопасность: rate‑limit логина/регистрации, защита от брутфорса, капча.
- Больше тестов: очереди улучшений, авторизация, негативные кейсы.
- CI/CD: линт, тесты, сборка образов, деплой.
- Наблюдаемость: Prometheus‑метрики/экспортер, централизованные логи.
- История версий резюме с откатом и сравнением.

## FAQ и рекомендации

> 401 Unauthorized

- Проверьте заголовок: `Authorization: Bearer <token>` и срок действия токена.

> CORS в разработке

- Добавьте origin фронтенда в `CORS_ORIGINS` или используйте same‑origin через Nginx.

> Миграции

- Перед запуском API в Docker выполняется `alembic upgrade head` (см. `infrastructure/docker-compose.yml`).

> Flower

- Чтобы открыть снаружи, добавьте `ports: - "5555:5555"` сервису `flower` и перезапустите compose.
