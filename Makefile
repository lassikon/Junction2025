.PHONY: help up down build restart logs clean migrate db-upgrade db-downgrade db-status db-history

help:
	@echo "Available commands:"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build all containers"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Remove containers and volumes"
	@echo ""
	@echo "Database Migration commands:"
	@echo "  make migrate MSG='description'  - Create new migration"
	@echo "  make db-upgrade                 - Apply all pending migrations"
	@echo "  make db-downgrade              - Rollback last migration"
	@echo "  make db-status                 - Show current migration version"
	@echo "  make db-history                - Show migration history"

up:
	docker-compose up

down:
	docker-compose down

build:
	docker-compose up --build

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

# Database migration commands
migrate:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: Please provide a migration message using MSG='your message'"; \
		echo "Example: make migrate MSG='add user age field'"; \
		exit 1; \
	fi
	cd backend && alembic revision --autogenerate -m "$(MSG)"

db-upgrade:
	cd backend && alembic upgrade head

db-downgrade:
	cd backend && alembic downgrade -1

db-status:
	cd backend && alembic current

db-history:
	cd backend && alembic history --verbose
