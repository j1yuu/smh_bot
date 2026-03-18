# Unified OpenAI Terminal Bot

## Что делает приложение

Это единый терминальный бот на базе OpenAI API, который умеет:

- вести обычный диалог в интерактивном режиме;
- вызывать инструмент получения текущего времени;
- по запросу пользователя читать текстовый файл, парсить его в строгую JSON-схему и сохранять результат в указанный JSON-файл;
- запускаться как чат-бот или как одноразовый CLI-парсер.

Архитектура разделена на отдельные компоненты:

- `Config` — централизованная конфигурация из `.env` и переменных окружения;
- `ParserService` — сервис парсинга текста и файлов через OpenAI Responses API;
- `ToolRegistry`, `CurrentTimeTool`, `ParseFileTool` — набор инструментов, доступных агенту;
- `Agent` — чат-агент, который управляет диалогом и вызовами инструментов;
- `cli.py` — единая CLI-точка входа.

## Структура проекта

```text
main.py
src/
  main.py              # запуск приложения через src-совместимый entrypoint
  app/
    agent.py
    cli.py
    config.py
    models.py
    openai_support.py
    parser_service.py
    schemas.py
    tools.py
tests/
  conftest.py          # автоматически добавляет src/ в sys.path для pytest
  test_main.py
  test_unified_bot.py
```

## Требования

- Python 3.10+
- Установленные пакеты:
  - `openai`
  
Пример установки:

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai
```

> Загрузка `.env` реализована внутри приложения, отдельная библиотека для этого не требуется.

## Конфигурация

Создайте `.env` файл по примеру `.env.example`:

```env
OPENAI_API_KEY=your_api_key
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_PARSER_MODEL=gpt-4.1
OPENAI_REQUEST_TIMEOUT_SECONDS=60
OPENAI_MAX_RETRIES=3
OPENAI_RETRY_DELAY_SECONDS=1
```

Дополнительно можно переопределять:

- `BOT_SYSTEM_PROMPT`
- `PARSER_SYSTEM_PROMPT`

## Запуск

### 1. Интерактивный чат

```bash
python main.py chat
```

или через src-совместимый entrypoint:

```bash
python src/main.py chat
```

### 2. Разовый парсинг файла

```bash
python main.py parse data/input.txt data/output.json
```

или:

```bash
python src/main.py parse data/input.txt data/output.json
```

## Пример диалога

```text
Вы: который час?
Бот: Сейчас 2026-03-18 12:00:00 UTC.

Вы: спарси файл ./examples/order.txt и сохрани в ./out/order.json
Бот: Готово, файл обработан и JSON сохранён в /absolute/path/out/order.json.
```

## Отказоустойчивость

В приложение добавлены базовые механизмы надёжности:

- проверка наличия `OPENAI_API_KEY` при старте;
- повторные попытки запросов к OpenAI с задержкой;
- валидация аргументов инструментов;
- проверка существования входного файла;
- автоматическое создание директории для выходного файла;
- строгая JSON-схема для результата парсинга.

## Тесты

```bash
pytest
```

Если нужен встроенный раннер `unittest`, он тоже продолжает работать:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
