.PHONY: help install test lint format typecheck check clean run dev

help:
	@echo "Piddy - Backend Developer AI Agent"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code with black"
	@echo "  make typecheck     - Run type checking with mypy"
	@echo "  make check         - Run all checks (lint, format, typecheck, test)"
	@echo "  make clean         - Remove cache and temporary files"
	@echo "  make run           - Run the application"
	@echo "  make dev           - Run in development mode with reload"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/
	black --check src/ tests/

format:
	black src/ tests/

typecheck:
	mypy src/

check: lint format typecheck test
	@echo "All checks passed!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist build *.egg-info

run:
	python -m src.main

dev:
	uvicorn src.main:create_app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t piddy:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env piddy:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down
