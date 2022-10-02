ifeq ($(shell test -e '.env' && echo -n yes), yes)
	include .env
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif



HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

help: ##@Help Show this help
	@echo -e "Usage: make [target] ... \n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

db: ##@Database Create database with docker-compose
	@docker-compose -f docker-compose.yml up -d --remove-orphans database redis

migrate: ##@Database Do all migrations n database
	alembic upgrade $(args)

revision: ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_34sdf23f_message.py)
	alembic revision --autogenerate

run-all: ##@Application Run all in docker compose
	@docker-compose up -d --remove-orphans

run:
	@source ./.env && poetry run bot

logs: ##@Application Show docker compose logs
	@docker-compose logs -f

%::
	echo $(MESSAGE)