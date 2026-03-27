# ============================================
# Makefile — Django DRF Project Commands
# ============================================

.PHONY: help install run migrate makemigrations test superuser shell lint flush collectstatic

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -r requirements.txt --break-system-packages

run: ## Start Django development server
	python3 manage.py runserver 0.0.0.0:8000

migrate: ## Run makemigrations and migrate
	python3 manage.py makemigrations
	python3 manage.py migrate

makemigrations: ## Create new migrations
	python3 manage.py makemigrations

superuser: ## Create a superuser
	python3 manage.py createsuperuser

test: ## Run all tests with pytest
	pytest -v

test-cov: ## Run tests with coverage report
	pytest -v --cov=apps --cov-report=term-missing

shell: ## Open Django shell
	python3 manage.py shell

lint: ## Run code linting with ruff
	ruff check apps/

flush: ## Flush the database
	python3 manage.py flush --no-input

collectstatic: ## Collect static files
	python3 manage.py collectstatic --no-input
