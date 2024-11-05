import argparse
import logging

from alembic.config import CommandLine

from ecology_bot.adapters.database.config import DatabaseConfig
from ecology_bot.adapters.database.utils import make_alembic_config


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    alembic = CommandLine()
    alembic.parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    options = alembic.parser.parse_args()
    db_config = DatabaseConfig()
    if "cmd" not in options:
        alembic.parser.error("Too few arguments")
        exit(128)
    else:
        config = make_alembic_config(options, pg_url=db_config.master_dsn)
        alembic.run_cmd(config, options)
        exit()


if __name__ == "__main__":
    main()
