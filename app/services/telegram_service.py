import asyncio
import secrets

from loguru import logger

from app.core.config import settings


class TelegramService:
    def __init__(self) -> None:
        self.enabled = settings.TELEGRAM_ENABLED
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        logger.info(f'TelegramService инициализирован (enabled: {self.enabled})')

    async def send_telegram(
        self,
        chat_id: str,
        message: str,
    ) -> bool:
        if not self.enabled:
            logger.warning('🤖 Telegram отправка отключена')
            return False
        logger.info(f'Отправка Telegram сообщения в чат {chat_id}')
        logger.debug(f'Сообщение: {message[:100]}...')

        try:
            await asyncio.sleep(secrets.SystemRandom().uniform(0.1, 0.5))
            if secrets.SystemRandom().random() < 0.8:
                logger.info(f'Telegram сообщение успешно отправлено в чат {chat_id}')
                return True
            logger.warning(f'Mock: Не удалось отправить Telegram сообщение в чат {chat_id}')
            raise Exception(f'Mock ошибка отправки в Telegram чат {chat_id}')

        except Exception as e:
            logger.error(f'Ошибка отправки Telegram: {e!s}')
            raise Exception(f'Ошибка отправки Telegram: {e!s}')

    async def validate_chat_id(self, chat_id: str) -> bool:
        return len(chat_id) > 0 and (chat_id.startswith('@') or chat_id.isdigit())
