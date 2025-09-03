from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import install_error_handlers
from app.api.routes import auth as auth_routes
from app.api.routes import health as health_routes
from app.api.routes import improvements as improvements_routes
from app.api.routes import resume as resume_routes
from app.core.config import settings
from app.logging_config import setup_logging
from app.middleware.request_id import RequestIDMiddleware

setup_logging()
logger = logging.getLogger(__name__)

# Top-level OpenAPI description and tags
tags_metadata = [
    {
        "name": "auth",
        "description": "Регистрация и авторизация пользователей. Возвращает JWT access токены.",
    },
    {
        "name": "resume",
        "description": "CRUD-операции над резюме текущего пользователя.",
    },
    {
        "name": "improvements",
        "description": "Постановка в очередь улучшений резюме и получение статуса выполнения.",
    },
]

app = FastAPI(
    title="ResumeLab API",
    version="1.0.0",
    openapi_url="/openapi.json",
    description=(
        "Backend-сервис для работы с резюме: регистрация/логин, CRUD резюме, "
        "асинхронные улучшения с помощью Celery.\n\n"
        "Авторизация: передавайте заголовок `Authorization: Bearer <token>` для "
        "защищённых ручек.\n\n"
        "Секции:\n"
        "- auth — регистрация и получение токена;\n"
        "- resume — создание/получение/редактирование/удаление резюме;\n"
        "- improvements — постановка задачи на улучшение и получение статуса.\n\n"
        "Идентификатор запроса `X-Request-ID` можно задать на входе; он будет "
        "возвращён в ответе и попадёт в логи."
    ),
    openapi_tags=tags_metadata,
    contact={
        "name": "ResumeLab",
        "url": "https://example.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_error_handlers(app)


@app.middleware("http")
async def inject_user_id(request: Request, call_next):
    # user id is set within route dependencies where available
    response = await call_next(request)
    return response


app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(resume_routes.router, prefix=settings.API_PREFIX)
app.include_router(improvements_routes.router, prefix=settings.API_PREFIX)
app.include_router(improvements_routes.alt_router, prefix=settings.API_PREFIX)
app.include_router(health_routes.router)
