import json
import os
from datetime import datetime

from openai import OpenAI


SYSTEM_PROMPT = (
    "Ты — полезный чат-бот для терминала. "
    "Если пользователь спрашивает текущее время, дату, который час или похожие вещи, "
    "ты можешь вызвать функцию get_current_time. "
    "Для остальных вопросов отвечай обычным текстом."
)


def get_current_time() -> str:
    """Возвращает текущее локальное время в читаемом формате."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


TOOLS = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "Возвращает текущее локальное время пользователя в формате YYYY-MM-DD HH:MM:SS",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    }
]


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_chat() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Не найден OPENAI_API_KEY. Установите переменную окружения перед запуском.")

    print("Терминальный чат запущен. Для выхода напишите: exit")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        user_text = input("Вы: ").strip()

        if user_text.lower() in {"exit", "quit", "выход"}:
            print("Бот: До встречи!")
            break

        messages.append({"role": "user", "content": user_text})

        first_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = first_response.choices[0].message

        if assistant_message.tool_calls:
            messages.append(
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
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments or "{}")

                if function_name == "get_current_time":
                    result = get_current_time()
                else:
                    result = f"Неизвестная функция: {function_name}"

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            {
                                "function": function_name,
                                "arguments": arguments,
                                "result": result,
                            },
                            ensure_ascii=False,
                        ),
                    }
                )

            second_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
            )
            final_text = second_response.choices[0].message.content
            messages.append({"role": "assistant", "content": final_text})
            print(f"Бот: {final_text}")
        else:
            final_text = assistant_message.content or "Без ответа"
            messages.append({"role": "assistant", "content": final_text})
            print(f"Бот: {final_text}")


if __name__ == "__main__":
    run_chat()
