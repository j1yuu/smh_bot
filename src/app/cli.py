from __future__ import annotations

import argparse
from typing import Sequence

from .agent import Agent
from .config import Config
from .openai_support import OpenAIClientFactory
from .parser_service import ParserService
from .tools import CurrentTimeTool, ParseFileTool, ToolRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Единый терминальный чат-бот с OpenAI и встроенным парсером файлов."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    chat_parser = subparsers.add_parser("chat", help="Запустить интерактивный чат")
    chat_parser.set_defaults(handler=run_chat)

    parse_parser = subparsers.add_parser("parse", help="Разово распарсить файл в JSON")
    parse_parser.add_argument("input_path", help="Путь к входному текстовому файлу")
    parse_parser.add_argument("output_path", help="Путь к выходному JSON-файлу")
    parse_parser.set_defaults(handler=run_parse)

    return parser


def create_services() -> tuple[Config, ParserService, ToolRegistry, Agent]:
    config = Config.from_env()
    client = OpenAIClientFactory.create(config)
    parser_service = ParserService(client, config)
    tools = ToolRegistry([CurrentTimeTool(), ParseFileTool(parser_service)])
    agent = Agent(client, config, tools)
    return config, parser_service, tools, agent


def run_chat(_args: argparse.Namespace) -> int:
    _, _, _, agent = create_services()
    agent.run_interactive()
    return 0


def run_parse(args: argparse.Namespace) -> int:
    _, parser_service, _, _ = create_services()
    result = parser_service.parse_file(args.input_path, args.output_path)
    print(f"Готово. JSON сохранён в: {result.output_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except KeyboardInterrupt:
        print("Остановлено пользователем.")
        return 130
    except Exception as error:  # noqa: BLE001
        print(f"Ошибка: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
