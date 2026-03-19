#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"
DEPS_STAMP="${VENV_DIR}/.deps_installed"
PYTHON_BIN="${PYTHON_BIN:-python3}"

unset ALL_PROXY all_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Не найден интерпретатор ${PYTHON_BIN}. Установите Python 3."
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[setup] Создаю виртуальное окружение в ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

if [[ ! -f "${DEPS_STAMP}" || "${REQUIREMENTS_FILE}" -nt "${DEPS_STAMP}" ]]; then
  echo "[setup] Устанавливаю зависимости"
  python -m pip install --disable-pip-version-check -r "${REQUIREMENTS_FILE}"
  touch "${DEPS_STAMP}"
fi

if [[ ! -f "${PROJECT_ROOT}/.env" && -f "${PROJECT_ROOT}/.env.example" ]]; then
  cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
  echo "[setup] Создан .env из .env.example. Добавьте OPENAI_API_KEY перед первым запуском."
fi

exec python "${PROJECT_ROOT}/main.py" "$@"
