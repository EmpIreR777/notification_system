from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.notifications_router import router as notifications_router
from app.core.config import settings
from app.core.logger_config import setup_logger

logger = setup_logger(
    log_dir='logs',
    log_file='debug.log',
    log_level=settings.LOG_LEVEL,
    rotation='100 MB',
    retention='10 days',
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Управление жизненным циклом приложения"""
    logger.info('Запуск системы уведомлений...')
    yield
    logger.info('Остановка системы уведомлений...')


# Создание приложения
app = FastAPI(
    title='Система уведомлений',
    description='FastAPI сервис для отправки уведомлений через Email, SMS и Telegram с fallback механизмом',
    version='1.0.0',
    lifespan=lifespan,
    docs_url='/docs',
    redoc_url='/redoc',
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(notifications_router, prefix='/api/v1', tags=['notifications'])


@app.get('/')
async def root() -> dict[str, str]:
    """Корневой эндпоинт"""
    return {'message': 'Система уведомлений работает!', 'version': '1.0.0', 'docs': '/docs'}


@app.get('/health')
async def health_check() -> dict[str, Any]:
    """Проверка работоспособности"""
    return {
        'status': 'healthy',
        'services': {
            'email': settings.EMAIL_ENABLED,
            'sms': settings.SMS_ENABLED,
            'telegram': settings.TELEGRAM_ENABLED,
        },
    }
