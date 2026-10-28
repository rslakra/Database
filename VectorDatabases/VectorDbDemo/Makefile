PYTHON ?= python3
ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV := $(ROOT)venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python
JUPYTER := $(VENV)/bin/jupyter
KERNEL_NAME := vector-db-demo
UV_BIN_PATH ?= $(HOME)/.local/bin/uv

.DEFAULT_GOAL := help

.PHONY: help setup uv venv install kernel notebook clean

help: ## Show available commands
	@echo "VectorDbDemo"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "First-time setup:"
	@echo "  make setup"
	@echo "  source venv/bin/activate"
	@echo "  make notebook"
	@echo ""
	@echo "Note: uv (system CLI) and pip (.venv packages) are separate — setup uses pip, not uv pip."

setup: uv venv install kernel ## Install uv CLI, create .venv, pip install, register kernel

uv: ## Install uv CLI on your system (optional; does not manage .venv)
	@uv_bin_path="$(UV_BIN_PATH)"; \
	uv_dir="$$(dirname "$$uv_bin_path")"; \
	if command -v uv >/dev/null 2>&1; then \
		echo "uv: installed ($$(command -v uv))"; \
		uv --version; \
	elif [ -f "$$uv_bin_path" ]; then \
		echo "uv: installed ($$uv_bin_path)"; \
		echo "note: add $$uv_dir to PATH if 'uv' is not found in your shell"; \
		"$$uv_bin_path" --version; \
	else \
		echo "uv: not installed — installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "uv: installed at $$uv_bin_path"; \
		"$$uv_bin_path" --version; \
	fi

venv: ## Create Python virtual environment (.venv/) with pip
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@echo "Virtual environment ready: $(VENV)"

install: venv ## Install dependencies from requirements.txt with pip
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

kernel: install ## Register .venv as Jupyter kernel ($(KERNEL_NAME))
	$(PYTHON_VENV) -m ipykernel install --user --name=$(KERNEL_NAME) --display-name="Vector DB Demo"

notebook: install ## Launch Jupyter notebook in this directory
	cd $(ROOT) && $(JUPYTER) notebook

clean: ## Remove .venv and Python cache files
	rm -rf $(VENV)
	find $(ROOT) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find $(ROOT) -type f -name '*.py[co]' -delete 2>/dev/null || true
