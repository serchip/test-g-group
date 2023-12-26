CURRENT_DIRECTORY := $(shell pwd)

SERVICE = app

ifndef DC_FILE
	DC_FILE := docker-compose.yaml
endif

DC_CMD = docker-compose -f ${DC_FILE}

# Makefile target args
args = $(filter-out $@,$(MAKECMDGOALS))


migrate:
	$(DC_CMD) run --rm migrations alembic upgrade head

migrate-rollback:
	$(DC_CMD) run --rm migrations alembic downgrade -1

history:
	$(DC_CMD) run --rm migrations alembic history

migrations:
	$(DC_CMD) run --rm migrations alembic revision --autogenerate -m "$(MESSAGE)"

start: migrate
	$(DC_CMD) up -d

up:
	$(DC_CMD) run -p 8000:80 $(SERVICE) hypercorn --bind 0.0.0.0:80 --reload app.main:app

stop:
	$(DC_CMD) down

status:
	$(DC_CMD) ps

restart: stop start

cli:
	$(DC_CMD) exec $(SERVICE) bash

tail:
	$(DC_CMD) logs -f $(SERVICE)

build:
	$(DC_CMD) build

create_admin:
	$(DC_CMD) run --rm $(SERVICE) python3 app/create_admin.py

test:
	$(DC_CMD) up pytests
