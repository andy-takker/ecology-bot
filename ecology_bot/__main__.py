import logging

from aiomisc import Service, entrypoint
from aiomisc_log import basic_config

log = logging.getLogger(__name__)


def main() -> None:
    config = ...
    basic_config(level=config.log.level)

    services: list[Service] = [
        BotService(config=config),
    ]
    with entrypoint(
        *services,
        log_level=config.log.level,
        log_format=config.log.format,
        pool_size=config.database.pool_size,
        debug=config.app.debug,
    ) as loop:
        log.info("Starting services")
        loop.run_forever()


if __name__ == "__main__":
    main()
