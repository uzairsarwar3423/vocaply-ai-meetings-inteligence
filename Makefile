.PHONY: help build up down restart logs ps shell db-migrate db-revision

help:
	@echo "Usage:"
	@echo "  make build          Build the docker images"
	@echo "  make up             Start the docker containers"
	@echo "  make down           Stop the docker containers"
	@echo "  make restart        Restart the docker containers"
	@echo "  make logs           View the docker logs"
	@echo "  make ps             List the docker containers"
	@echo "  make shell          Open a shell in the backend container"
	@echo "  make db-migrate     Run database migrations"
	@echo "  make db-revision    Create a new database migration"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

shell:
	docker compose exec backend bash

db-migrate:
	docker compose exec backend alembic upgrade head

db-revision:
	@read -p "Enter revision message: " msg; \
	docker compose exec backend alembic revision --autogenerate -m "$$msg"
