PROJECT_NAME ?= ecology_bot
TEST_FOLDER_NAME ?= tests
PYTHON_VERSION ?= 3.11


develop: clean_dev ##@Develop Create virtualenv
	python$(PYTHON_VERSION) -m venv .venv
	.venv/bin/pip install -U pip poetry
	.venv/bin/poetry config virtualenvs.create false
	.venv/bin/poetry install
	.venv/bin/pre-commit install

local: ##@Develop Run dev containers for test
	docker compose -f docker-compose.dev.yaml up --force-recreate --renew-anon-volumes --build

format: ##@Code Reformat code with black
	poetry run python3 -m black $(APPLICATION_NAME)

migrate: ##@Database Do all migrations n database
	poetry run python3 -m alembic upgrade $(args)

revision: ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_34sdf23f_message.py)
	poetry run python3 -m alembic revision --autogenerate

run: ##@Application Run all in docker compose with build
	@docker-compose up -d --build --remove-orphans

run_bot:
	@source ./.env && poetry run bot

logs: ##@Application Show docker compose logs
	@docker-compose logs -f

clean_dev: ##@Develop Remove virtualenv
	rm -rf .venv

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ... \n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)
