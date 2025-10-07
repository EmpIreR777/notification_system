from enum import Enum


class NotificationChannel(str, Enum):
    EMAIL = 'email'
    SMS = 'sms'
    TELEGRAM = 'telegram'


class NotificationStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    RETRYING = 'retrying'


class NotificationPriority(str, Enum):
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'
