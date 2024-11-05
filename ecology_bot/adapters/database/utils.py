import os
from argparse import Namespace
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Final

import sqlalchemy.dialects.postgresql as pg
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

PROJECT_PATH: Final = Path(__file__).parent.parent.parent


@asynccontextmanager
async def create_engine(dsn: str, debug: bool) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        url=dsn,
        echo=debug,
        pool_size=15,
        max_overflow=10,
        pool_pre_ping=True,
    )
    yield engine
    await engine.dispose()


def create_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


def make_alembic_config(
    cmd_opts: Namespace, pg_url: str, base_path: Path = PROJECT_PATH
) -> Config:
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = str(base_path / "adapters/database" / cmd_opts.config)

    config = Config(
        file_=cmd_opts.config,
        ini_section=cmd_opts.name,
        cmd_opts=cmd_opts,
    )

    alembic_location = config.get_main_option("script_location")
    if not alembic_location:
        raise ValueError

    if not os.path.isabs(alembic_location):
        config.set_main_option("script_location", str(base_path / alembic_location))

    config.set_main_option("sqlalchemy.url", pg_url)
    config.attributes["configure_logger"] = False

    return config


def make_pg_enum(enum_cls: type[Enum], **kwargs: Any) -> pg.ENUM:
    return pg.ENUM(
        enum_cls,
        values_callable=_choices,
        **kwargs,
    )


def _choices(enum_cls: type[Enum]) -> tuple[str, ...]:
    return tuple(map(str, enum_cls))
