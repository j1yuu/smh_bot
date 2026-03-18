# Unified OpenAI Terminal Bot

Около 90% кода написано нейросетью.

## Что делает приложение

Это единый терминальный бот на базе OpenAI API, который умеет:

- вести обычный диалог в интерактивном режиме;
- вызывать инструмент получения текущего времени;
- по запросу пользователя читать текстовый файл, парсить его в строгую JSON-схему и сохранять результат в указанный JSON-файл;
- запускаться как чат-бот или как одноразовый CLI-парсер.

## Запуск из коробки

### Вариант 1. Один скрипт для установки и запуска

```bash
./run.sh chat
```

Что делает `run.sh` автоматически:

1. создаёт виртуальное окружение `.venv`, если его ещё нет;
2. устанавливает зависимости из `requirements.txt`;
3. создаёт `.env` из `.env.example`, если `.env` ещё отсутствует;
4. запускает приложение через `python main.py ...`.

Если нужен разовый парсинг файла:

```bash
./run.sh parse example_input.txt output.json
```

> После первого автосоздания `.env` обязательно добавьте в него `OPENAI_API_KEY`.

### Вариант 2. Команды через Makefile

Подготовка окружения:

```bash
make setup
```

Запуск чата:

```bash
make chat
```

Разовый парсинг файла:

```bash
make parse INPUT=example_input.txt OUTPUT=output.json
```

Запуск тестов:

```bash
make test
```

## Ручная конфигурация

Если хотите настроить всё вручную, создайте `.env` файл по примеру `.env.example`:

```env
# ключ доступа к OpenAI API
OPENAI_API_KEY=

# модели по умолчанию
OPENAI_CHAT_MODEL=
OPENAI_PARSER_MODEL=

# устойчивость запросов
OPENAI_REQUEST_TIMEOUT_SECONDS=60
OPENAI_MAX_RETRIES=3
OPENAI_CHAT_MAX_TOKENS=2048
OPENAI_RETRY_DELAY_SECONDS=1
```

## Прямой запуск приложения

### 1. Интерактивный чат

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
