from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.enum import NotificationChannel, NotificationPriority, NotificationStatus


class NotificationRequest(BaseModel):
    email: str = Field(..., description='Email')
    phone: str = Field(..., description='Номер телефона')
    telegram_id: str = Field(..., description='Telegram ID')
    subject: str = Field(..., max_length=255, description='Тема уведомления')
    message: str = Field(..., max_length=2000, description='Текст сообщения')
    channels: list[NotificationChannel] = Field(
        default=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.TELEGRAM]
    )
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL)

    @field_validator('email')
    def validate_recipient(cls, v: str | None) -> str | None:
        if not v or len(v.strip()) == 0:
            raise ValueError('Получатель не может быть пустым')
        return v.strip()

    @field_validator('channels')
    def validate_channels(cls, v: list[str] | None) -> list[str] | None:
        if not v or len(v) == 0:
            raise ValueError('Должен быть указан хотя бы один канал')
        return v


class NotificationResponse(BaseModel):
    id: str = Field(..., description='Уникальный ID уведомления')
    status: NotificationStatus = Field(...)
    successful_channels: list[NotificationChannel] = Field(default_factory=list)
    failed_channels: list[NotificationChannel] = Field(default_factory=list)
    attempts: dict[str, int] = Field(default_factory=dict)
    error_details: dict[str, str] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sent_at: datetime | None = None


class NotificationHistory(BaseModel):
    id: str
    email: str
    subject: str
    message: str
    channels: list[NotificationChannel]
    status: NotificationStatus
    successful_channels: list[NotificationChannel]
    failed_channels: list[NotificationChannel]
    created_at: datetime
    sent_at: datetime | None
    error_details: dict[str, str] | None

    class Config:
        from_attributes = True
