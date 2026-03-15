.PHONY: setup dev down

setup:
	docker compose up -d
	pip install -r requirements.txt

dev:
	uvicorn main:app --reload
down:
	docker compose down
