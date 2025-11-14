.PHONY: help up down build restart logs clean

help:
	@echo "Available commands:"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make build      - Build all containers"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs"
	@echo "  make clean      - Remove containers and volumes"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose up --build -d

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f
