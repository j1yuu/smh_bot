from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.agent import Agent
from app.config import Config
from app.models import ToolExecutionResult
from app.parser_service import ParserService
from app.tools import CurrentTimeTool, ParseFileTool, ToolRegistry


class ParserServiceTests(unittest.TestCase):
    def test_parse_file_writes_json_output(self) -> None:
        mock_client = Mock()
        mock_client.responses.create.return_value = SimpleNamespace(
            output_text=json.dumps({"items": [{"title": "Milk", "quantity": "1", "price": "100"}]})
        )
        config = Config(openai_api_key="test")
        service = ParserService(mock_client, config)

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "input.txt"
            output_path = Path(tmp_dir) / "out.json"
            input_path.write_text("milk 1 100", encoding="utf-8")

            result = service.parse_file(input_path, output_path)

            self.assertEqual(result.payload["items"][0]["title"], "Milk")
            self.assertTrue(output_path.exists())


class AgentTests(unittest.TestCase):
    def test_agent_executes_tool_and_returns_follow_up_text(self) -> None:
        config = Config(openai_api_key="test")
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="",
                            tool_calls=[
                                SimpleNamespace(
                                    id="tool-1",
                                    function=SimpleNamespace(
                                        name="get_current_time",
                                        arguments="{}",
                                    ),
                                )
                            ],
                        )
                    )
                ]
            ),
            SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Сейчас 2026-01-01 00:00:00 UTC", tool_calls=None))]
            ),
        ]

        class FixedTool:
            name = "get_current_time"

            def definition(self) -> dict[str, object]:
                return {"type": "function", "function": {"name": self.name, "parameters": {}}}

            def execute(self, arguments_json: str) -> ToolExecutionResult:
                _ = arguments_json
                return ToolExecutionResult(self.name, {"current_time": "2026-01-01 00:00:00 UTC"})

        registry = ToolRegistry([FixedTool()])
        agent = Agent(mock_client, config, registry)

        answer = agent.respond("Который час?")

        self.assertIn("2026-01-01", answer)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)


class ParseFileToolTests(unittest.TestCase):
    def test_parse_file_tool_requires_arguments(self) -> None:
        parser_service = Mock()
        tool = ParseFileTool(parser_service)

        with self.assertRaises(ValueError):
            tool.execute("{}")


if __name__ == "__main__":
    unittest.main()
