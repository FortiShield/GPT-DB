.DEFAULT_GOAL := help

SHELL := /bin/bash
PYTHON := 3.11
VENV := .venv.make

# -------------------------
# Packages
# -------------------------
PACKAGES := \
	gptdb-accelerator \
	gptdb-client \
	gptdb-ext \
	gptdb-serve \
	gptdb-app \
	gptdb-core \
	gptdb-sandbox

PKG ?=

# -------------------------
# OS / venv handling
# -------------------------
ifeq ($(OS),Windows_NT)
	VENV_BIN := $(VENV)/Scripts
else
	VENV_BIN := $(VENV)/bin
endif

# -------------------------
# Virtualenv
# -------------------------
setup: $(VENV)/.venv-timestamp ## Setup dev virtualenv

$(VENV)/.venv-timestamp: uv.lock
	uv venv --python $(PYTHON) $(VENV)
	uv pip install --prefix $(VENV) ruff mypy pytest
	touch $@

# -------------------------
# Sync deps
# -------------------------
testenv: setup ## Sync dependencies
	. $(VENV_BIN)/activate && uv sync --all-packages \
		--extra base \
		--extra proxy_openai \
		--extra rag \
		--extra storage_chromadb \
		--extra gptdbs \
		--link-mode=copy
	cp .devcontainer/gptdb.pth $(VENV)/lib/python$(PYTHON)/site-packages || true

# -------------------------
# Formatting
# -------------------------
fmt: setup ## Format code
	$(VENV_BIN)/ruff format packages examples i18n scripts
	$(VENV_BIN)/ruff check --select I --fix packages examples i18n scripts
	$(VENV_BIN)/ruff check --fix packages \
		--exclude="packages/gptdb-serve/src/**"

fmt-check: setup ## Check formatting
	$(VENV_BIN)/ruff format --check packages examples
	$(VENV_BIN)/ruff check --select I packages examples

# -------------------------
# Tests
# -------------------------
test: testenv ## Run all tests
	$(VENV_BIN)/pytest --pyargs gptdb

test-%: testenv ## Run tests for a single package
	$(VENV_BIN)/pytest packages/$*/tests

all-test: $(addprefix test-,$(PACKAGES)) ## Test all packages

# -------------------------
# Mypy
# -------------------------
mypy: testenv ## Run mypy
	$(VENV_BIN)/mypy --config-file .mypy.ini packages/gptdb-core

# -------------------------
# Build
# -------------------------
build: clean-dist ## Build all packages
	uv build --all-packages

build-%: ## Build a single package
	cd packages/$* && uv sync && uv build

all-build: $(addprefix build-,$(PACKAGES)) ## Build all packages individually

# -------------------------
# Docker
# -------------------------
docker-%: ## Build docker image for a package
	cd packages/$* && docker build -t gptdb/$*:latest .

all-docker: $(addprefix docker-,$(PACKAGES)) ## Docker build all packages

# -------------------------
# Publish
# -------------------------
publish: build ## Publish all packages to PyPI
	uv publish

publish-test: build ## Publish to TestPyPI
	uv publish --index testpypi

publish-%: build-% ## Publish a single package
	cd packages/$* && uv publish

# -------------------------
# Clean
# -------------------------
clean: ## Clean env
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

clean-dist: ## Clean build artifacts
	rm -rf dist build *.egg-info

# -------------------------
# Help
# -------------------------
help: ## Show help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' \
	| sort
