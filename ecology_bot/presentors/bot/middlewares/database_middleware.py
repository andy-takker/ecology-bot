from aiocache import Cache
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from ecology_bot.presentors.bot.services.repo import Repo


class DatabaseMiddleware(LifetimeControllerMiddleware):
    def __init__(self, async_session_maker, cache: Cache):
        super().__init__()
        self.async_session_maker = async_session_maker
        self.cache = cache

    async def pre_process(self, obj, data, *args):
        session: AsyncSession = self.async_session_maker()
        data["session"] = session
        data["repo"] = Repo(session=session, cache=self.cache)

    async def post_process(self, obj, data, *args):
        del data["repo"]
        session: AsyncSession = data.get("session")
        await session.close()
