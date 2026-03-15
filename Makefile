.PHONY: setup dev down

PYTHON := python3
VENV := venv
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

setup:
	docker compose up -d
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt

dev:
	$(UVICORN) main:app --reload

down:
	docker compose down
