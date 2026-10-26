.PHONY: up down build test-book test-order

up:
	docker compose up --build -d

down:
	docker compose down -v

build:
	docker compose build

test-book:
	cd book_service && pytest tests/ -v

test-order:
	cd order_service && pytest tests/ -v
