import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env")

from openai import OpenAI
from openai.types import ResponsesModel

MODEL: ResponsesModel = "gpt-4.1"

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "quantity": {"type": "string"},
                    "price": {"type": "string"},
                },
                "required": ["title", "quantity", "price"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = (
    "Ты преобразуешь сырой текст в JSON. "
    "Извлеки список сущностей из текста. "
    "Для каждого элемента верни поля title, quantity, price. "
    "Если какого-то значения нет в тексте, запиши 'unknown'. "
    "Ничего не выдумывай и не добавляй лишних полей."
)


def parse_text_to_json(raw_text: str) -> dict:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "parsed_items",
                "schema": SCHEMA,
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)

def main() -> None:
    if len(sys.argv) != 3:
        print("Использование: python parser_to_json.py <input.txt> <output.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Ошибка: файл {input_path} не найден")
        sys.exit(1)

    raw_text = input_path.read_text(encoding="utf-8")

    try:
        result = parse_text_to_json(raw_text)
    except Exception as e:
        print(f"Ошибка при обращении к OpenAI API: {e}")
        sys.exit(1)

    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Готово. JSON сохранён в: {output_path}")


if __name__ == "__main__":
    main()
