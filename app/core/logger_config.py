import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = 'importlib' in filename and '_bootstrap' in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger(
    log_dir: str = 'logs',
    log_file: str = 'app.log',
    log_level: str = 'INFO',
    rotation: str = '100 MB',
    retention: str = '7 days',
) -> Any:
    """
    Настройка логгера для приложения.

    Параметры:
    - log_dir: Директория для хранения логов
    - log_file: Имя файла логов
    - log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    - rotation: Правило ротации логов (например, "100 MB" или "1 week")
    - retention: Правило хранения логов (например, "7 days")
    """

    # Удаляем стандартные обработчики loguru
    logger.remove()

    # Создаем директорию для логов, если её нет
    Path(log_dir).mkdir(exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # Настройка вывода в КОНСОЛЬ
    form = (
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<level>{level: <8}</level> | <cyan>{name}</cyan>:'
        '<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    )
    logger.add(
        sys.stdout,
        format=form,
        level=log_level,
        colorize=True,
        enqueue=True,
        backtrace=True,
    )

    # Настройка записи в ФАЙЛ с ротацией
    logger.add(
        log_path,
        format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} \
            | {name}:{function}:{line} - {message}',
        level=log_level,
        rotation=rotation,
        retention=retention,
        enqueue=True,
        compression='zip',
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)

    if log_level != 'DEBUG':
        logging.getLogger('uvicorn.access').disabled = True

    logging.getLogger('aiohttp.client').setLevel(log_level)
    logging.getLogger('aiohttp.internal').setLevel(log_level)
    logging.getLogger('fastapi').setLevel(log_level)
    logging.getLogger('uvicorn.error').setLevel(log_level)

    return logger
