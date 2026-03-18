from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from json import JSONDecodeError, dumps, loads
from typing import Any, Protocol

from .models import ToolExecutionResult
from .parser_service import ParserService


class Tool(Protocol):
    name: str

    def definition(self) -> dict[str, Any]: ...

    def execute(self, arguments_json: str) -> ToolExecutionResult: ...


@dataclass(slots=True)
class CurrentTimeTool:
    name: str = "get_current_time"

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Возвращает текущее UTC-время в формате YYYY-MM-DD HH:MM:SS",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
            },
        }

    def execute(self, arguments_json: str) -> ToolExecutionResult:
        _ = arguments_json
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return ToolExecutionResult(
            name=self.name,
            content={"current_time": current_time},
        )


@dataclass(slots=True)
class ParseFileTool:
    parser_service: ParserService
    name: str = "parse_file_to_json"

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (
                    "Читает текстовый файл, отправляет его в OpenAI для парсинга "
                    "и сохраняет результат в JSON-файл."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input_path": {
                            "type": "string",
                            "description": "Относительный или абсолютный путь к входному текстовому файлу.",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Относительный или абсолютный путь к выходному JSON-файлу.",
                        },
                    },
                    "required": ["input_path", "output_path"],
                    "additionalProperties": False,
                },
            },
        }

    def execute(self, arguments_json: str) -> ToolExecutionResult:
        try:
            arguments = loads(arguments_json or "{}")
        except JSONDecodeError as error:
            raise ValueError(f"Некорректный JSON аргументов для {self.name}: {error}") from error

        input_path = arguments.get("input_path")
        output_path = arguments.get("output_path")
        if not isinstance(input_path, str) or not isinstance(output_path, str):
            raise ValueError("Для parse_file_to_json требуются строковые input_path и output_path.")

        result = self.parser_service.parse_file(input_path, output_path)
        return ToolExecutionResult(
            name=self.name,
            content={
                "input_path": str(result.input_path),
                "output_path": str(result.output_path),
                "items_count": len(result.payload.get("items", [])),
                "result_preview": result.payload,
            },
        )


class ToolRegistry:
    def __init__(self, tools: list[Tool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    @property
    def definitions(self) -> list[dict[str, Any]]:
        return [tool.definition() for tool in self._tools.values()]

    def execute(self, name: str, arguments_json: str) -> ToolExecutionResult:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(f"Неизвестный инструмент: {name}")
        return tool.execute(arguments_json)

    @staticmethod
    def error_result(name: str, error: Exception) -> ToolExecutionResult:
        return ToolExecutionResult(name=name, content={"error": str(error)})

    @staticmethod
    def serialize_result(result: ToolExecutionResult) -> str:
        return dumps(result.content, ensure_ascii=False)
