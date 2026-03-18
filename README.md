# Unified OpenAI Terminal Bot

Около 90% кода написано нейросетью.

## Что делает приложение

Это единый терминальный бот на базе OpenAI API, который умеет:

- вести обычный диалог в интерактивном режиме;
- вызывать инструмент получения текущего времени;
- по запросу пользователя читать текстовый файл, парсить его в строгую JSON-схему и сохранять результат в указанный JSON-файл;
- запускаться как чат-бот или как одноразовый CLI-парсер.

## Конфигурация

Создайте `.env` файл по примеру `.env.example`:

```env
# ключ доступа к OpenAI API
OPENAI_API_KEY=

# модели по умолчанию
OPENAI_CHAT_MODEL=
OPENAI_PARSER_MODEL=

# устойчивость запросов
OPENAI_REQUEST_TIMEOUT_SECONDS=60
OPENAI_MAX_RETRIES=3
OPENAI_CHAT_MAX_TOKENS=20000
OPENAI_RETRY_DELAY_SECONDS=1
```

## Запуск

### 1. Интерактивный чат

Самый удобный вариант:

```bash
python main.py chat
```

Также можно запускать так:

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

## Тесты

Тесты настроены так, чтобы их можно было запускать прямо из корня проекта без ручной настройки `PYTHONPATH`:

```bash
python -m unittest discover -s tests
```

При желании можно запустить и отдельный файл:

```bash
python -m unittest tests/test_unified_bot.py
```
