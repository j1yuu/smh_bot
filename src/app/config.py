from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Config:
    """Application configuration loaded from environment variables."""

    openai_api_key: str
    chat_model: str = "gpt-4.1-mini"
    parser_model: str = "gpt-4.1"
    request_timeout_seconds: float = 60.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    system_prompt: str = (
        "Ты — полезный терминальный чат-бот. "
        "Поддерживай обычный диалог, а при необходимости вызывай доступные инструменты. "
        "Для запросов про текущее время используй функцию get_current_time. "
        "Для запросов на парсинг файлов используй функцию parse_file_to_json. "
        "Если путь к файлу не указан, сначала уточни его у пользователя."
    )
    parser_system_prompt: str = (
        "Ты преобразуешь сырой текст в JSON. "
        "Извлеки список сущностей из текста. "
        "Для каждого элемента верни поля title, quantity, price. "
        "Если какого-то значения нет в тексте, запиши 'unknown'. "
        "Ничего не выдумывай и не добавляй лишних полей."
    )

    @classmethod
    def from_env(cls, env_file: str | Path = ".env") -> "Config":
        cls._load_dotenv_file(env_file)

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "Не найден OPENAI_API_KEY. Добавьте его в переменные окружения или в .env файл."
            )

        return cls(
            openai_api_key=api_key,
            chat_model=os.getenv("OPENAI_CHAT_MODEL", cls.chat_model),
            parser_model=os.getenv("OPENAI_PARSER_MODEL", cls.parser_model),
            request_timeout_seconds=float(
                os.getenv("OPENAI_REQUEST_TIMEOUT_SECONDS", cls.request_timeout_seconds)
            ),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", cls.max_retries)),
            retry_delay_seconds=float(
                os.getenv("OPENAI_RETRY_DELAY_SECONDS", cls.retry_delay_seconds)
            ),
            system_prompt=os.getenv("BOT_SYSTEM_PROMPT", cls.system_prompt),
            parser_system_prompt=os.getenv(
                "PARSER_SYSTEM_PROMPT", cls.parser_system_prompt
            ),
        )

    @staticmethod
    def _load_dotenv_file(env_file: str | Path) -> None:
        path = Path(env_file)
        if not path.exists() or not path.is_file():
            return

        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
