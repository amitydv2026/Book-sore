.PHONY: install test run

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
