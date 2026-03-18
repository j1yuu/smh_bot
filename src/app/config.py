from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CHAT_MODEL = "gpt-4.1-mini"
DEFAULT_PARSER_MODEL = "gpt-4.1"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 1.0
DEFAULT_SYSTEM_PROMPT = (
    "Ты — полезный терминальный чат-бот. "
    "Поддерживай обычный диалог, а при необходимости вызывай доступные инструменты. "
    "Для запросов про текущее время используй функцию get_current_time. "
    "Для запросов на парсинг файлов используй функцию parse_file_to_json. "
    "Если путь к файлу не указан, сначала уточни его у пользователя."
)
DEFAULT_PARSER_SYSTEM_PROMPT = (
    "Ты преобразуешь сырой текст в JSON. "
    "Извлеки список сущностей из текста. "
    "Для каждого элемента верни поля title, quantity, price. "
    "Если какого-то значения нет в тексте, запиши 'unknown'. "
    "Ничего не выдумывай и не добавляй лишних полей."
)


@dataclass(slots=True)
class Config:
    """Application configuration loaded from environment variables."""

    openai_api_key: str
    chat_model: str = DEFAULT_CHAT_MODEL
    parser_model: str = DEFAULT_PARSER_MODEL
    request_timeout_seconds: float = DEFAULT_REQUEST_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay_seconds: float = DEFAULT_RETRY_DELAY_SECONDS
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    parser_system_prompt: str = DEFAULT_PARSER_SYSTEM_PROMPT

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
            chat_model=os.getenv("OPENAI_CHAT_MODEL", DEFAULT_CHAT_MODEL),
            parser_model=os.getenv("OPENAI_PARSER_MODEL", DEFAULT_PARSER_MODEL),
            request_timeout_seconds=float(
                os.getenv(
                    "OPENAI_REQUEST_TIMEOUT_SECONDS",
                    str(DEFAULT_REQUEST_TIMEOUT_SECONDS),
                )
            ),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", str(DEFAULT_MAX_RETRIES))),
            retry_delay_seconds=float(
                os.getenv("OPENAI_RETRY_DELAY_SECONDS", str(DEFAULT_RETRY_DELAY_SECONDS))
            ),
            system_prompt=os.getenv("BOT_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
            parser_system_prompt=os.getenv(
                "PARSER_SYSTEM_PROMPT", DEFAULT_PARSER_SYSTEM_PROMPT
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
