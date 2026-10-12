.PHONY: help lint test check

help: ## Show targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-8s %s\n", $$1, $$2}'

lint: ## Ruff lint + format check, mypy
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

test: ## Run pytest
	uv run pytest

check: lint test ## lint + test
