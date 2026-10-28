# PostgreSQL Docker — mirrors docker-compose.yml
#
# All compose variables can be overridden:
#   make start DATA_DIR=$HOME/postgres-data POSTGRES_PORT=5433

.DEFAULT_GOAL := help

COMPOSE           := docker compose
SERVICE           := postgresql
UI_SERVICE        := postgres-admin
CONTAINER         := postgres
DATA_DIR          ?= $(CURDIR)/data
POSTGRES_USER     ?= postgres
POSTGRES_PASSWORD ?= postgres
POSTGRES_DB       ?= dummy
POSTGRES_PORT     ?= 5432
UI_PORT           ?= 8080

export POSTGRES_DATA_DIR := $(DATA_DIR)
export POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_PORT

.PHONY: help data-dir start stop restart status health health-ui logs logs-ui psql shell url ui adminer clean

help: ## Show available targets
	@echo "PostgreSQL 18 + pgweb (Docker)"
	@echo "  DB service:  $(SERVICE)  (container: $(CONTAINER))"
	@echo "  Web UI:      $(UI_SERVICE)  → http://localhost:$(UI_PORT)"
	@echo "  Data dir:    $(POSTGRES_DATA_DIR)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables (make VAR=value or export before compose):"
	@echo "  DATA_DIR          Host path → /var/lib/postgresql (PG 18+)  ($(DATA_DIR))"
	@echo "  POSTGRES_PORT     PostgreSQL host port                    ($(POSTGRES_PORT))"
	@echo "  POSTGRES_USER     Superuser                               ($(POSTGRES_USER))"
	@echo "  POSTGRES_PASSWORD Initial password (first boot only)      ($(POSTGRES_PASSWORD))"
	@echo "  POSTGRES_DB       Default database (first boot only)      ($(POSTGRES_DB))"
	@echo "  UI_PORT           Web UI host port (compose fixed)        ($(UI_PORT))"
	@echo ""
	@echo "Examples:"
	@echo "  make start"
	@echo "  make start DATA_DIR=$$HOME/postgres-data"
	@echo "  make ui           # print Web UI URL"

data-dir: ## Create / show the host data directory
	@mkdir -p "$(POSTGRES_DATA_DIR)"
	@echo "Data directory: $(POSTGRES_DATA_DIR)"
	@ls -la "$(POSTGRES_DATA_DIR)" 2>/dev/null || true

start: data-dir ## Start PostgreSQL + web UI (waits until DB accepts connections)
	@test -n "$(POSTGRES_DATA_DIR)" || (echo "ERROR: POSTGRES_DATA_DIR is empty" && exit 1)
	$(COMPOSE) up -d --wait
	@echo ""
	@echo "PostgreSQL ready"
	@echo "  URL:      postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@localhost:$(POSTGRES_PORT)/$(POSTGRES_DB)"
	@echo "  Data dir: $(POSTGRES_DATA_DIR)"
	@echo ""
	@echo "Web UI: http://localhost:$(UI_PORT)  (pgweb — opens connected, no login form)"

stop: ## Stop all services (data on disk is kept)
	$(COMPOSE) down
	@echo "Stopped. Data remains at: $(POSTGRES_DATA_DIR)"

restart: stop start ## Restart PostgreSQL + web UI

status: ## Show container status
	$(COMPOSE) ps

health: ## Check PostgreSQL TCP on 127.0.0.1 (inside DB container)
	@docker exec $(CONTAINER) pg_isready -h 127.0.0.1 -p 5432 -U $(POSTGRES_USER) -d $(POSTGRES_DB) \
		&& echo "PostgreSQL TCP is ready." \
		|| (echo "PostgreSQL not ready — run: make logs" && exit 1)

health-ui: ## Check pgweb is serving and connected to PostgreSQL
	@curl -sf "http://localhost:$(UI_PORT)/api/info" >/dev/null \
		&& echo "Web UI is up and connected to PostgreSQL." \
		|| (echo "Web UI not ready — run: make logs-ui && make restart" && exit 1)

health-adminer: health-ui ## Alias for health-ui (backwards compat)

logs: ## Follow PostgreSQL logs
	$(COMPOSE) logs -f $(SERVICE)

logs-ui: ## Follow web UI logs
	$(COMPOSE) logs -f $(UI_SERVICE)

logs-adminer: logs-ui ## Alias for logs-ui (backwards compat)

psql: ## Open psql inside the container
	docker exec -it $(CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

shell: ## Open a shell inside the PostgreSQL container
	docker exec -it $(CONTAINER) bash

url: ## Print PostgreSQL connection URL
	@echo "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@localhost:$(POSTGRES_PORT)/$(POSTGRES_DB)"

ui: ## Print web UI URL
	@echo "Open: http://localhost:$(UI_PORT)"
	@echo "Database: $(POSTGRES_DB)  (pgweb connects automatically — no login form)"

adminer: ui ## Alias for ui (backwards compat)

clean: ## Stop and DELETE all data in DATA_DIR (destructive)
	@echo "WARNING: This removes all database files in:"
	@echo "  $(POSTGRES_DATA_DIR)"
	@printf "Type 'yes' to continue: " && read ans && [ "$$ans" = "yes" ] || (echo "Aborted." && exit 1)
	$(COMPOSE) down --remove-orphans 2>/dev/null || true
	rm -rf "$(POSTGRES_DATA_DIR)"
	@echo "Data removed. Run 'make start' to initialize a fresh database."
