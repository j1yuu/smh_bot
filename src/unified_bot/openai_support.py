from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from .config import Config

if TYPE_CHECKING:
    from openai import OpenAI

T = TypeVar("T")


class OpenAIClientFactory:
    @staticmethod
    def create(config: Config) -> OpenAI:
        from openai import OpenAI

        return OpenAI(api_key=config.openai_api_key, timeout=config.request_timeout_seconds)


def with_retries(
    operation: Callable[[], T],
    *,
    max_retries: int,
    retry_delay_seconds: float,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as error:  # noqa: BLE001
            last_error = error
            if attempt >= max_retries:
                break
            time.sleep(retry_delay_seconds * attempt)

    if last_error is None:
        raise RuntimeError("Операция OpenAI завершилась без результата.")
    raise RuntimeError(f"Ошибка после {max_retries} попыток: {last_error}") from last_error
