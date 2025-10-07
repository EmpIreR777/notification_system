import asyncio
import secrets
from collections.abc import Callable
from functools import wraps
from typing import Any

from loguru import logger


def retry_async(
    max_attempts: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, exceptions: tuple[type, ...] = (Exception,)
) -> Callable[..., Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: dict[str, Any]) -> Any:
            last_exception = None
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:  # type: ignore
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f'Попытки исчерпаны для {func.__name__}: {e!s}')
                        raise

                    jitter_amount = secrets.SystemRandom().uniform(0.1, 0.3) * current_delay
                    sleep_time = min(current_delay + jitter_amount, 60.0)
                    logger.warning(
                        f'Попытка {attempt} не удалась для {func.__name__}: {e!s}. Повтор через {sleep_time:.2f}с'
                    )
                    await asyncio.sleep(sleep_time)
                    current_delay *= backoff_factor
            raise last_exception  # type: ignore

        return wrapper

    return decorator


class RetryConfig:
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter = jitter


async def retry_with_config(func: Callable[..., Any], config: RetryConfig, *args: Any, **kwargs: dict[str, Any]) -> Any:
    last_exception = None
    current_delay = config.initial_delay
    for attempt in range(1, config.max_attempts + 1):
        try:
            logger.debug(f'Попытка {attempt}/{config.max_attempts} для {getattr(func, "__name__", str(func))}')
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            if attempt > 1:
                logger.info(f'Успешно после {attempt} попыток: {getattr(func, "__name__", str(func))}')

            return result
        except Exception as e:
            last_exception = e
            if attempt == config.max_attempts:
                logger.error(f'Попытки исчерпаны для {func.__name__}: {e!s}')
                raise

            if config.jitter:
                jitter_amount = secrets.SystemRandom().uniform(0.1, 0.3) * current_delay
                sleep_time = min(current_delay + jitter_amount, config.max_delay)
            else:
                sleep_time = min(current_delay, config.max_delay)

            logger.warning(
                f'Попытка {attempt} не удалась для {getattr(func, "__name__", str(func))}: {e!s}. Повтор через {
                    sleep_time:.2f}с'
            )
            await asyncio.sleep(sleep_time)
            current_delay *= config.backoff_factor

    raise last_exception  # type: ignore
