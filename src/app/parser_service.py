from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .config import Config
from .models import ParseResult
from .openai_support import with_retries
from .schemas import PARSER_SCHEMA

if TYPE_CHECKING:
    from openai import OpenAI


class ParserService:
    """Service that converts raw text into a strict JSON structure."""

    def __init__(self, client: OpenAI, config: Config) -> None:
        self._client = client
        self._config = config

    def parse_text(self, raw_text: str) -> dict[str, Any]:
        def _request() -> Any:
            return self._client.responses.create(
                model=self._config.parser_model,
                input=[
                    {"role": "system", "content": self._config.parser_system_prompt},
                    {"role": "user", "content": raw_text},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "parsed_items",
                        "schema": PARSER_SCHEMA,
                        "strict": True,
                    }
                },
            )

        response = with_retries(
            _request,
            max_retries=self._config.max_retries,
            retry_delay_seconds=self._config.retry_delay_seconds,
        )
        return json.loads(response.output_text)

    def parse_file(self, input_path: str | Path, output_path: str | Path) -> ParseResult:
        resolved_input = Path(input_path).expanduser().resolve()
        resolved_output = Path(output_path).expanduser().resolve()

        if not resolved_input.exists():
            raise FileNotFoundError(f"Входной файл не найден: {resolved_input}")
        if not resolved_input.is_file():
            raise IsADirectoryError(f"Ожидался файл, а не директория: {resolved_input}")

        raw_text = resolved_input.read_text(encoding="utf-8")
        payload = self.parse_text(raw_text)

        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return ParseResult(
            input_path=resolved_input,
            output_path=resolved_output,
            payload=payload,
        )
