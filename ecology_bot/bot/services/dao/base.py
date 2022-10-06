import abc

from aiocache import Cache
from sqlalchemy.ext.asyncio import AsyncSession


class DAO(abc.ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession, cache: Cache | None = None):
        self.session = session
        self.cache = cache
