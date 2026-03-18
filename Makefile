PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
RUNNER := ./run.sh

.PHONY: setup chat parse test

setup:
	$(RUNNER) --help >/dev/null

chat:
	$(RUNNER) chat

parse:
	@if [ -z "$(INPUT)" ] || [ -z "$(OUTPUT)" ]; then \
		echo 'Использование: make parse INPUT=example_input.txt OUTPUT=out.json'; \
		exit 1; \
	fi
	$(RUNNER) parse $(INPUT) $(OUTPUT)

test:
	$(RUNNER) --help >/dev/null
	$(VENV_PYTHON) -m unittest discover -s tests
