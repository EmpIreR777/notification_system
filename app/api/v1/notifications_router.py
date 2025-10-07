from fastapi import APIRouter, HTTPException, Path, Query
from loguru import logger
from pyparsing import Any

from app.schemas.notification_schemas import (
    NotificationRequest,
    NotificationResponse,
)
from app.services.notification_service import notification_service

router = APIRouter()


@router.post(
    '/notifications',
    response_model=NotificationResponse,
    summary='Отправить уведомление',
)
async def send_notification(request: NotificationRequest) -> NotificationResponse:
    try:
        logger.info(f'Получен запрос на отправку уведомления: {request.email}')
        return await notification_service.send_notification(request)
    except ValueError as e:
        logger.error(f'Ошибка валидации данных: {e!s}')
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f'Неожиданная ошибка: {e!s}')
        raise HTTPException(status_code=500, detail='internal_error')


@router.get(
    '/notifications/{notification_id}',
    response_model=NotificationResponse | None,
    summary='Получить статус уведомления',
)
async def get_notification_status(
    notification_id: str = Path(..., description='ID уведомления'),
) -> NotificationResponse | None:
    try:
        response = await notification_service.get_notification_status(notification_id)
        if response is None:
            raise HTTPException(status_code=404, detail='notification_not_found')
        return response
    except ValueError as e:
        logger.error(f'Ошибка валидации данных: {e!s}')
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f'Ошибка получения статуса уведомления: {e!s}')
        raise HTTPException(status_code=500, detail='internal_error')


@router.get(
    '/notifications',
    response_model=list[NotificationResponse],
    summary='Получить историю уведомлений',
)
async def get_notification_history(
    limit: int = Query(default=50, ge=1, le=1000, description='Количество уведомлений'),
) -> list[NotificationResponse]:
    try:
        return await notification_service.get_notification_history(limit=limit)
    except Exception as e:
        logger.error(f'Ошибка получения истории уведомлений: {e!s}')
        raise HTTPException(status_code=500, detail='internal_error')


@router.post(
    '/notifications/test',
    response_model=dict,
    summary='Тестовая отправка уведомления',
)
async def send_test_notification() -> dict[str, Any]:
    try:
        request = NotificationRequest(
            email='test@example.com',
            phone='+79652567890',
            telegram_id='123456789',
            subject='Test notification',
            message='This is a test',
        )
        response = await notification_service.send_notification(request)
        return {'ok': True, 'id': response.id}
    except Exception as e:
        logger.error(f'Ошибка отправки тестового уведомления: {e!s}')
        raise HTTPException(status_code=500, detail='internal_error')
