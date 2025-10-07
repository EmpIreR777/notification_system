SHELL := /bin/bash

# =============================================================================
# BUILD
# =============================================================================
.PHONY: sync-all  ## Create .venv and add all dependencies from pyproject.toml
sync-all:
	uv sync --all-groups

.PHONY: alembic-rev  ## Создание автомиграций с message из консоли
alembic-rev:
	./alembic_rev.sh "$(m)"

.PHONY: alembic-up  ## Обновление HEAD
alembic-up:
	uv run alembic upgrade head

.PHONY: alembic-down  ## downgrade -1
alembic-down:
	uv run alembic downgrade -1

# =============================================================================
# DEV SERVER
# =============================================================================
.PHONY: run-server
run-server:
	uv run migrations.py
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# =============================================================================
# DOCKER
# =============================================================================
.PHONY: psql  ## Open an lca_email_sender container on psql
psql:
	docker exec -it postgres psql -d lca_payment_yookassa -U postgres

# =============================================================================
# TEST AND LINT
# =============================================================================
.PHONY: pre-commit-install
pre-commit-install:
	uv run pre-commit install --install-hooks

.PHONY: lint
lint:
	uv run pre-commit run --all-files

.PHONY: ruff
ruff:
	uv run ruff check --fix

.PHONY: mypy
mypy:
	uv run mypy .

# Очистка всех кешей Python
clean-cache:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find .. -type d -name .ruff_cache -exec rm -rf {} +
