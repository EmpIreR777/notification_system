from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PATH_TO_ENV = Path(__file__).parent.parent.resolve().joinpath('.env')


class Settings(BaseSettings):
    """Настройки приложения"""

    # Общие настройки
    DEBUG: bool = True
    LOG_LEVEL: str = 'INFO'
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 2

    # Email настройки
    EMAIL_ENABLED: bool = True
    EMAIL_HOST: str = 'smtp.gmail.com'
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str | None = None
    EMAIL_PASSWORD: str | None = None
    EMAIL_USE_TLS: bool = True

    # SMS настройки
    SMS_ENABLED: bool = True
    SMS_PROVIDER: str = 'mock'

    # Telegram настройки
    TELEGRAM_ENABLED: bool = True
    TELEGRAM_BOT_TOKEN: str | None = None

    model_config = SettingsConfigDict(env_file=str(PATH_TO_ENV), extra='ignore')


settings = Settings()
