import asyncio
import re
import secrets

from loguru import logger

from app.core.config import settings


class SMSService:
    def __init__(self) -> None:
        self.enabled = settings.SMS_ENABLED
        self.provider = settings.SMS_PROVIDER
        logger.info(f'SMSService инициализирован (enabled: {self.enabled}, provider: {self.provider})')

    async def send_sms(
        self,
        phone: str,
        message: str,
    ) -> bool:
        if not self.enabled:
            logger.warning('SMS отправка отключена')
            return False

        logger.info(f'Отправка SMS to={phone}')
        logger.debug(f'Сообщение: {message[:100]}...')

        try:
            await asyncio.sleep(secrets.SystemRandom().uniform(0.1, 0.5))
            if secrets.SystemRandom().random() < 0.8:
                logger.info(f'SMS успешно отправлен to={phone}')
                return True
            logger.warning(f'Mock: не удалось отправить SMS to={phone}')
            raise Exception(f'Mock ошибка отправки SMS {phone}')

        except Exception as e:
            logger.error(f'Ошибка отправки SMS: {e!s}')
            raise Exception(str(e))

    async def validate_phone_number(self, phone: str) -> bool:
        digits_only = re.sub(r'\D', '', phone)
        return 7 <= len(digits_only) <= 15
