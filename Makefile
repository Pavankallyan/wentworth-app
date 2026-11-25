# Wentworth App — shortcuts
#
#   make setup   create .venv and install dependencies
#   make test    run the pytest suite (DB is mocked, no MySQL needed)
#   make run     start the Flask dev server on http://127.0.0.1:5000
#   make clean   remove the virtual environment and caches

PY ?= python3
VENV ?= .venv
VENV_BIN := $(VENV)/bin

.PHONY: setup test run clean

setup:
	$(PY) -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt

test:
	$(VENV_BIN)/python -m pytest tests/ -v

run:
	$(VENV_BIN)/python app.py

clean:
	rm -rf $(VENV) .pytest_cache tests/__pycache__ __pycache__
