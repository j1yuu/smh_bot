from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .config import Config
from .openai_support import with_retries
from .tools import ToolRegistry

if TYPE_CHECKING:
    from openai import OpenAI

Message = dict[str, Any]


class Agent:
    """Interactive terminal agent backed by OpenAI chat completions."""

    def __init__(self, client: OpenAI, config: Config, tools: ToolRegistry) -> None:
        self._client = client
        self._config = config
        self._tools = tools
        self._messages: list[Message] = [
            {"role": "system", "content": self._config.system_prompt},
        ]

    def run_interactive(self) -> None:
        print("Терминальный чат запущен. Для выхода напишите: exit")
        while True:
            user_text = input("Вы: ").strip()
            if user_text.lower() in {"exit", "quit", "выход"}:
                print("Бот: До встречи!")
                return
            answer = self.respond(user_text)
            print(f"Бот: {answer}")

    def respond(self, user_text: str) -> str:
        self._messages.append({"role": "user", "content": user_text})
        return self._complete_with_tools()

    def _complete_with_tools(self) -> str:
        response = with_retries(
            self._create_completion,
            max_retries=self._config.max_retries,
            retry_delay_seconds=self._config.retry_delay_seconds,
        )
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            self._messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call in assistant_message.tool_calls
                    ],
                }
            )

            for tool_call in assistant_message.tool_calls:
                try:
                    result = self._tools.execute(
                        tool_call.function.name,
                        tool_call.function.arguments or "{}",
                    )
                except Exception as error:  # noqa: BLE001
                    result = self._tools.error_result(tool_call.function.name, error)

                self._messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": self._tools.serialize_result(result),
                    }
                )

            follow_up = with_retries(
                self._create_completion,
                max_retries=self._config.max_retries,
                retry_delay_seconds=self._config.retry_delay_seconds,
            )
            final_text = follow_up.choices[0].message.content or "Без ответа"
            self._messages.append({"role": "assistant", "content": final_text})
            return final_text

        final_text = assistant_message.content or "Без ответа"
        self._messages.append({"role": "assistant", "content": final_text})
        return final_text

    def _create_completion(self) -> Any:
        return self._client.chat.completions.create(
            model=self._config.chat_model,
            messages=self._messages,
            tools=self._tools.definitions,
            tool_choice="auto",
        )
