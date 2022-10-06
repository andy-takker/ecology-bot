from functools import lru_cache

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from ecology_bot.database import Base


@lru_cache
def get_admin_db() -> SQLAlchemy:
    db = SQLAlchemy(metadata=Base.metadata)
    return db


def get_engine(db_url: str) -> Engine:
    engine = create_async_engine(
        db_url, pool_size=20, max_overflow=0, poolclass=QueuePool
    )
    return engine


def get_async_session_maker(db_url: str) -> sessionmaker:
    engine = get_engine(db_url=db_url)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
