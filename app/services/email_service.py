import asyncio
import secrets

from loguru import logger

from app.core.config import settings


class EmailService:
    def __init__(self) -> None:
        self.enabled = settings.EMAIL_ENABLED
        logger.info(f'EmailService инициализирован (enabled: {self.enabled})')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
    ) -> bool:
        if not self.enabled:
            logger.warning('Email отправка отключена')
            return False

        logger.info(f'Отправка email to={to_email} subject={subject}')
        logger.debug(f'Сообщение: {message[:100]}...')

        try:
            await asyncio.sleep(secrets.SystemRandom().uniform(0.1, 0.5))
            if secrets.SystemRandom().random() < 0.8:
                logger.info(f'Email успешно отправлен to={to_email}')
                return True
            logger.warning(f'Mock: не удалось отправить Email to={to_email}')
            return False

        except Exception as e:
            logger.error(f'Ошибка отправки Email: {e!s}')
            raise RuntimeError(f'Ошибка отправки Email: {e!s}')

    async def validate_email(self, email: str) -> bool:
        return '@' in email and '.' in email
