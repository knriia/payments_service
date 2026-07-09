.PHONY: help up down logs restart shell ps build rebuild down-v ps-a migrate create_migration downgrade rollback_to

ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
SERVICE := $(firstword $(ARGS))

ifneq ($(ARGS),)
$(ARGS):
	@:
endif

help:
	@echo "Available commands:"
	@echo ""
	@echo "  make up [services...]              Start containers"
	@echo "  make build [services...]           Build containers"
	@echo "  make rebuild [services...]         Rebuild containers without cache"
	@echo "  make down                          Stop and remove containers"
	@echo "  make down-v                        Stop and remove containers with volumes"
	@echo "  make logs [services...]            Show logs"
	@echo "  make restart [services...]         Restart containers"
	@echo "  make shell <service>               Open shell in service"
	@echo "  make ps                            Show running containers"
	@echo "  make ps-a                          Show all containers"
	@echo "  make migrate                       Apply migrations"
	@echo "  make downgrade                     Rollback last migration (-1)"
	@echo "  make rollback_to <revision_id>     Rollback to specific revision ID"
	@echo "  make create_migration <name>       Create new alembic migration"
	@echo ""
	@echo "Examples:"
	@echo "  make up"
	@echo "  make up api postgres"
	@echo "  make logs api"
	@echo "  make shell api"
	@echo "  make create_migration init_db"
	@echo "  make migrate"
	@echo "  make downgrade"
	@echo "  make rollback_to 5cef681a714a"

up:
	docker compose up -d $(ARGS)

build:
	docker compose build $(ARGS)

rebuild:
	docker compose build --no-cache $(ARGS)

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f $(ARGS)

restart:
	docker compose restart $(ARGS)

shell:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Ошибка: Укажите имя сервиса. Пример: make shell api"; \
		exit 1; \
	fi
	docker compose exec $(SERVICE) bash

ps:
	docker compose ps

ps-a:
	docker compose ps -a

migrate:
	docker compose run --rm migrations

create_migration:
	@if [ -z "$(ARGS)" ]; then \
		echo "Ошибка: укажи название миграции. Пример: make create_migration init_db"; \
		exit 1; \
	fi
	docker compose run --rm migrations alembic revision --autogenerate -m "$(ARGS)"

downgrade:
	docker compose run --rm migrations alembic downgrade -1

rollback_to:
	@if [ -z "$(ARGS)" ]; then \
		echo "Ошибка: укажи ID миграции. Пример: make rollback_to 5cef681a714a"; \
		exit 1; \
	fi
	docker compose run --rm migrations alembic downgrade $(ARGS)
