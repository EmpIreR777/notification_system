import uuid
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from app.schemas.notification_schemas import (
    NotificationChannel,
    NotificationRequest,
    NotificationResponse,
    NotificationStatus,
)
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.telegram_service import TelegramService
from app.utils.retry import retry_async


class NotificationService:
    def __init__(self) -> None:
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.telegram_service = TelegramService()
        self.notification_history: dict[str, NotificationResponse] = {}
        self.channel_services = {
            NotificationChannel.EMAIL: self.email_service,
            NotificationChannel.SMS: self.sms_service,
            NotificationChannel.TELEGRAM: self.telegram_service,
        }
        logger.info('NotificationService инициализирован')

    async def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        notification_id = str(uuid.uuid4())
        logger.info(f'Начинаем отправку уведомления {notification_id}')
        logger.info(f'Получатель: {request.email}')
        logger.info(f'Каналы: {[c.value for c in request.channels]}')

        response = NotificationResponse(
            id=notification_id,
            status=NotificationStatus.PENDING,
            successful_channels=[],
            failed_channels=[],
            attempts={},
        )

        successful_channels = []
        failed_channels = []
        error_details: dict[str, str] = {}

        for channel in request.channels:
            service = self.channel_services.get(channel)
            try:
                ok = await self._send_with_retry(service, channel, request, notification_id)
                response.attempts[channel.value] = response.attempts.get(channel.value, 0) + 1
                if ok:
                    successful_channels.append(channel)
                    response.sent_at = datetime.now(UTC)
                    break
                failed_channels.append(channel)
            except Exception as e:
                failed_channels.append(channel)
                error_details[channel.value] = str(e)

        response.successful_channels = successful_channels
        response.failed_channels = failed_channels
        response.error_details = error_details if error_details else None

        if successful_channels:
            response.status = NotificationStatus.SENT
            logger.info(f'Уведомление {notification_id} успешно отправлено')
        else:
            response.status = NotificationStatus.FAILED
            logger.error(f'Уведомление {notification_id} не было отправлено ни одним каналом')
            raise RuntimeError(f'Уведомление {notification_id} не было отправлено ни одним каналом')

        self.notification_history[notification_id] = response
        return response

    @retry_async(max_attempts=3, delay=2)
    async def _send_with_retry(
        self, service: Any, channel: NotificationChannel,
        request: NotificationRequest, notification_id: str
    ) -> bool:
        try:
            if channel == NotificationChannel.EMAIL:
                return await service.send_email(request.email, request.subject, request.message)
            if channel == NotificationChannel.SMS:
                return await service.send_sms(request.phone, request.message)
            if channel == NotificationChannel.TELEGRAM:
                return await service.send_telegram(request.telegram_id, request.message)
        except Exception:
            logger.exception(f'Ошибка отправки через {channel.value}')
            raise

        return False

    async def get_notification_status(self, notification_id: str) -> NotificationResponse | None:
        return self.notification_history.get(notification_id)

    async def get_notification_history(self, limit: int = 100) -> list[NotificationResponse]:
        history = list(self.notification_history.values())
        history.sort(key=lambda x: x.created_at, reverse=True)
        return history[:limit]


notification_service = NotificationService()
