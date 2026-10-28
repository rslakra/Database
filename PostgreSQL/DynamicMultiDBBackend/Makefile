# Dynamic Multi-DB Backend (FastAPI app: external PostgreSQL + optional Databricks)
#
#   make install
#   make run PORT=8001

.DEFAULT_GOAL := help

PYTHON ?= python3
VENV   ?= .venv
BIN    := $(VENV)/bin
HOST   ?= 127.0.0.1
PORT   ?= 8000

.PHONY: help venv install run check clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

venv: ## Create the virtual environment
	@test -x $(BIN)/python || $(PYTHON) -m venv --clear $(VENV)

install: venv ## Install dependencies
	$(BIN)/python -m pip install -r requirements.txt

run: ## Run the API (reads .env)
	@test -f .env || (echo "Missing .env - run: cp .env.sample .env" && exit 1)
	$(BIN)/python -m uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

check: ## Check the PostgreSQL connection using .env settings
	@test -f .env || (echo "Missing .env - run: cp .env.sample .env" && exit 1)
	@$(BIN)/python -c "from sqlalchemy import text; from app.database import postgres_engine as e; \
c = e.connect(); print(c.execute(text('SELECT current_user, current_database()')).one()); c.close()"

clean: ## Remove the virtual environment and caches
	rm -rf $(VENV)
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
