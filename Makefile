.PHONY: lint format format-check test-unit test-integration test-e2e test-all coverage

lint:
	ruff check src/

format:
	ruff format src/

format-check:
	ruff format --check src/

test-unit:
	cd src && python -m pytest tests/unit -v

test-integration:
	cd src && python -m pytest tests/integration -v

test-e2e:
	cd src && python -m pytest tests/e2e -v

test-all:
	cd src && python -m pytest tests/unit tests/integration tests/e2e -v

coverage:
	cd src && python -m pytest tests/unit tests/integration tests/e2e --cov=app --cov-report=xml --cov-report=term
