ifeq ($(shell test -e '.env' && echo -n yes), yes)
	include .env
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
	MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
	MESSAGE = "Done"
endif

APPLICATION_NAME = ecology_bot

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ... \n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

env: ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.dev .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env
	@echo "Note: you need add Telegram Bot Token!"

init: ##@Environment Init poetry project
	@poetry shell
	@poetry install
	@make env

db: ##@Database Create database with docker-compose
	@docker-compose -f docker-compose.yml up -d --remove-orphans db redis

format: ##@Code Reformat code with black
	poetry run python3 -m black $(APPLICATION_NAME)

migrate: ##@Database Do all migrations n database
	poetry run python3 -m alembic upgrade $(args)

revision: ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_34sdf23f_message.py)
	poetry run python3 -m alembic revision --autogenerate

requirements: ##@Application Update file `requirements.txt` with actual poetry packages
	poetry export --without-hashes --format=requirements.txt > requirements.txt

run: ##@Application Run all in docker compose with build
	@docker-compose up -d --build --remove-orphans

run_bot:
	@source ./.env && poetry run bot

logs: ##@Application Show docker compose logs
	@docker-compose logs -f

%::
	echo $(MESSAGE)