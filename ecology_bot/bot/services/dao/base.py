import abc

from sqlalchemy.ext.asyncio import AsyncSession


class DAO(abc.ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session
