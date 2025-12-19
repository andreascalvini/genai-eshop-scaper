.PHONY: help install install-dev test lint format clean run example

help:
	@echo "GenAI eShop Scraper - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make lint             - Run linters (ruff, mypy)"
	@echo "  make format           - Format code with black"
	@echo "  make test             - Run tests with pytest"
	@echo "  make clean            - Clean build artifacts"
	@echo ""
	@echo "Running:"
	@echo "  make example          - Run example crawl"
	@echo "  make run URL=<url>    - Crawl a specific URL"
	@echo ""
	@echo "Examples:"
	@echo "  make run URL=https://example.com/shop"
	@echo "  make example"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

lint:
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ --line-length=100

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache dist/ build/ *.egg-info
	rm -f products.json crawl_report.json

example:
	@echo "Running example crawl (simulated)..."
	@python example_usage.py

run:
	@if [ -z "$(URL)" ]; then \
		echo "Usage: make run URL=<url>"; \
		echo "Example: make run URL=https://example.com/shop"; \
		exit 1; \
	fi
	python -m src.main "$(URL)" products.json
	@echo ""
	@echo "Results saved to products.json and crawl_report.json"
	@echo "Products found: $$(jq '.total_products' products.json)"

.DEFAULT_GOAL := help
