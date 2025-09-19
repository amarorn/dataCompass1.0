.PHONY: help install dev test lint format build run docker-build docker-run docker-push clean

# Variables
PYTHON := python3
PIP := pip3
APP_NAME := datacompass-python
DOCKER_IMAGE := datacompass-python:latest
PORT := 3000

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov black flake8 mypy

dev: ## Run in development mode
	$(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port $(PORT)

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	$(PYTHON) -m flake8 src/
	$(PYTHON) -m mypy src/

format: ## Format code with black
	$(PYTHON) -m black src/ tests/

run: ## Run application
	$(PYTHON) src/main.py

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container
	docker run -p $(PORT):$(PORT) --env-file .env $(DOCKER_IMAGE)

docker-compose-up: ## Start services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop services with docker-compose
	docker-compose down

docker-compose-logs: ## Show docker-compose logs
	docker-compose logs -f

docker-push: ## Push Docker image to registry
	docker tag $(DOCKER_IMAGE) your-registry/$(DOCKER_IMAGE)
	docker push your-registry/$(DOCKER_IMAGE)

clean: ## Clean temporary files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.mypy_cache' -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

freeze: ## Freeze requirements
	$(PIP) freeze > requirements.txt

migrate: ## Run database migrations
	$(PYTHON) scripts/migrate.py

seed: ## Seed database with sample data
	$(PYTHON) scripts/seed.py

backup: ## Backup database
	$(PYTHON) scripts/backup.py

restore: ## Restore database from backup
	$(PYTHON) scripts/restore.py

logs: ## Show application logs
	tail -f logs/app.log

monitor: ## Monitor application metrics
	$(PYTHON) scripts/monitor.py
