from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from app.agent import Agent
from app.cli import main as cli_main
from app.config import Config
from app.models import ToolExecutionResult
from app.parser_service import ParserService
from app.tools import CurrentTimeTool, ParseFileTool, ToolRegistry


class ParserServiceTests(unittest.TestCase):
    def test_parse_file_writes_json_output(self) -> None:
        mock_client = Mock()
        mock_client.responses.create.return_value = SimpleNamespace(
            output_text=json.dumps({'items': [{'title': 'Milk', 'quantity': '1', 'price': '100'}]})
        )
        config = Config(openai_api_key='test')
        service = ParserService(mock_client, config)

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / 'input.txt'
            output_path = Path(tmp_dir) / 'out.json'
            input_path.write_text('milk 1 100', encoding='utf-8')

            result = service.parse_file(input_path, output_path)

            self.assertEqual(result.payload['items'][0]['title'], 'Milk')
            self.assertTrue(output_path.exists())


class ConfigTests(unittest.TestCase):
    def test_from_env_uses_string_defaults_instead_of_slot_descriptors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / 'test.env'
            env_path.write_text('OPENAI_API_KEY=test-key\n', encoding='utf-8')

            with patch.dict('os.environ', {}, clear=True):
                config = Config.from_env(env_path)

            self.assertEqual(config.chat_model, 'openai/gpt-4.1-nano')
            self.assertEqual(config.parser_model, 'openai/gpt-4.1-nano')
            self.assertIsInstance(config.request_timeout_seconds, float)
            self.assertEqual(config.max_retries, 3)


class ConfigTokenLimitTests(unittest.TestCase):
    def test_from_env_allows_overriding_chat_max_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / 'test.env'
            env_path.write_text(
                'OPENAI_API_KEY=test-key\nOPENAI_CHAT_MAX_TOKENS=512\n',
                encoding='utf-8',
            )

            with patch.dict('os.environ', {}, clear=True):
                config = Config.from_env(env_path)

            self.assertEqual(config.chat_max_tokens, 512)


class AgentTests(unittest.TestCase):
    def test_agent_executes_tool_and_returns_follow_up_text(self) -> None:
        config = Config(openai_api_key='test')
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='',
                            tool_calls=[
                                SimpleNamespace(
                                    id='tool-1',
                                    function=SimpleNamespace(
                                        name='get_current_time',
                                        arguments='{}',
                                    ),
                                )
                            ],
                        )
                    )
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='Сейчас 2026-01-01 00:00:00 UTC',
                            tool_calls=None,
                        )
                    )
                ]
            ),
        ]

        class FixedTool:
            name = 'get_current_time'

            def definition(self) -> dict[str, object]:
                return {'type': 'function', 'function': {'name': self.name, 'parameters': {}}}

            def execute(self, arguments_json: str) -> ToolExecutionResult:
                _ = arguments_json
                return ToolExecutionResult(self.name, {'current_time': '2026-01-01 00:00:00 UTC'})

        registry = ToolRegistry([FixedTool()])
        agent = Agent(mock_client, config, registry)

        answer = agent.respond('Который час?')

        self.assertIn('2026-01-01', answer)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        first_call_kwargs = mock_client.chat.completions.create.call_args_list[0].kwargs
        self.assertEqual(first_call_kwargs['max_tokens'], 2048)



class ParseFileToolTests(unittest.TestCase):
    def test_parse_file_tool_requires_arguments(self) -> None:
        parser_service = Mock()
        tool = ParseFileTool(parser_service)

        with self.assertRaises(ValueError):
            tool.execute('{}')


class CliTests(unittest.TestCase):
    @patch('app.cli.create_services')
    def test_chat_command_runs_interactive_agent(self, mock_create_services: Mock) -> None:
        mock_agent = Mock()
        mock_create_services.return_value = (Mock(), Mock(), Mock(), mock_agent)

        exit_code = cli_main(['chat'])

        self.assertEqual(exit_code, 0)
        mock_agent.run_interactive.assert_called_once_with()

    @patch('app.cli.create_services')
    @patch('builtins.print')
    def test_parse_command_prints_output_path(
        self,
        mock_print: Mock,
        mock_create_services: Mock,
    ) -> None:
        parser_service = Mock()
        parser_service.parse_file.return_value = SimpleNamespace(output_path='/tmp/out.json')
        mock_create_services.return_value = (Mock(), parser_service, Mock(), Mock())

        exit_code = cli_main(['parse', 'input.txt', 'output.json'])

        self.assertEqual(exit_code, 0)
        parser_service.parse_file.assert_called_once_with('input.txt', 'output.json')
        mock_print.assert_called_once_with('Готово. JSON сохранён в: /tmp/out.json')


if __name__ == '__main__':
    unittest.main()
