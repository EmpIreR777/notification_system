# Система уведомлений

FastAPI сервис для отправки уведомлений через Email, SMS и Telegram с fallback механизмом и повторными попытками.

## 🚀 Возможности

- **Мультиканальная отправка**: Email, SMS, Telegram
- **Fallback механизм**: Автоматический переход на следующий канал при неудаче
- **Повторные попытки**: Настраиваемый retry механизм с экспоненциальной задержкой
- **История уведомлений**: Отслеживание статуса отправленных уведомлений
- **Mock-режим**: Тестирование без реальной отправки сообщений
- **Подробное логирование**: Структурированные логи с ротацией

## 📦 Установка и запуск

### Предварительные требования

- Python 3.13+
- uv (современный менеджер пакетов Python)

### Установка

1. Установите зависимости:
```bash
make sync-all
```

2. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл под ваши настройки
```

3. Установите pre-commit хуки:
```bash
make pre-commit-install
```

### Запуск сервера

```bash
make run-server
```

Сервер будет доступен по адресу: http://localhost:8000

Документация API: http://localhost:8000/docs

## 🛠 API Endpoints

### Основные endpoints

- `POST /api/v1/notifications` - Отправить уведомление
- `GET /api/v1/notifications/{notification_id}` - Получить статус уведомления
- `GET /api/v1/notifications` - Получить историю уведомлений
- `POST /api/v1/notifications/test` - Тестовая отправка уведомления

### Вспомогательные endpoints

- `GET /` - Корневой эндпоинт
- `GET /health` - Проверка работоспособности сервиса


## 📋 Использование

### Пример отправки уведомления

```python
import requests
import json

url = "http://localhost:8000/api/v1/notifications"

payload = {
  "email": "to4ka@mail.ru",
  "phone": "+79628132233", 
  "telegram_id": "2314124",
  "subject": "Оповещение о готовносит",
  "message": "Ваши фотографии готовы, ждём вас.",
  "channels": ["email", "sms", "telegram"],
  "priority": "normal"
}

response = requests.post(url, json=payload)
print(response.json())
```

### Структура запроса

```json
{
  "email": "to4ka@mail.ru",
  "phone": "+79628132233", 
  "telegram_id": "2314124",
  "subject": "Оповещение о готовносит",
  "message": "Ваши фотографии готовы, ждём вас.",
  "channels": ["email", "sms", "telegram"],
  "priority": "normal"
}
```

## 🔧 Разработка

### Code Quality

Проект использует современные инструменты для обеспечения качества кода:

- **Ruff** - линтер и форматтер
- **Mypy** - проверка типов
- **Pre-commit** - автоматические проверки перед коммитом

### Доступные команды

```bash
make lint          # Запуск всех проверок
make ruff          # Запуск Ruff линтера
make mypy          # Проверка типов
make sync-all      # Обновление виртуального окружения
```

### Структура проекта

```
app/
├── api/v1/                    # API endpoints
│   └── notifications_router.py
├── core/                      # Основные настройки
│   ├── config.py
│   └── logger_config.py
├── schemas/                   # Pydantic схемы
│   └── notification_schemas.py
├── services/                  # Бизнес-логика
│   ├── notification_service.py
│   ├── email_service.py
│   ├── sms_service.py
│   └── telegram_service.py
├── utils/                     # Вспомогательные утилиты
│   └── retry.py
└── main.py                    # Точка входа
```

## 🧪 Тестирование

Для тестирования используйте встроенный тестовый endpoint:

```bash
    http://localhost:8000/docs
```

## 📊 Логирование

Логи сохраняются в директории `logs/` с ротацией:

- Ротация при достижении 100 MB
- Хранение логов в течение 10 дней
- Сжатие старых логов в ZIP архивы

## 🔄 Retry механизм

Сервис использует интеллектуальный retry механизм:

- Экспоненциальной задержкой между попытками
- Максимальным количеством попыток: 3
- Fallback на следующий канал при неудаче
