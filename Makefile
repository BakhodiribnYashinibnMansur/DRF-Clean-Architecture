# ============================================
# Makefile — Django DRF Project Commands (uv)
# ============================================

.PHONY: help install run migrate makemigrations test superuser shell lint flush collectstatic

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	uv sync --all-extras

run: ## Start Django development server
	uv run python manage.py runserver 0.0.0.0:8000

migrate: ## Run makemigrations and migrate
	uv run python manage.py makemigrations
	uv run python manage.py migrate

makemigrations: ## Create new migrations
	uv run python manage.py makemigrations

superuser: ## Create a superuser
	uv run python manage.py createsuperuser

test: ## Run all tests with pytest
	uv run pytest -v

test-cov: ## Run tests with coverage report
	uv run pytest -v --cov=apps --cov-report=term-missing

shell: ## Open Django shell
	uv run python manage.py shell

lint: ## Run code linting with ruff
	uv run ruff check apps/

flush: ## Flush the database
	uv run python manage.py flush --no-input

collectstatic: ## Collect static files
	uv run python manage.py collectstatic --no-input
