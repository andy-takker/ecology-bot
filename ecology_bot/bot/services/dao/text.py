from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer
from sqlalchemy import desc
from sqlalchemy.future import select

from ecology_bot.bot.services.dao.base import DAO
from ecology_bot.database.models import TextChunk


class TextChunkDAO(DAO):
    async def get_by_key(self, key: str) -> list[str]:
        q = (
            select(TextChunk.text)
            .where(TextChunk.key == key)
            .order_by(desc(TextChunk.weight))
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_text(self, key: str, sep: str = "\n", default: str = "") -> str:
        cache_key = "get_text" + key + "sep" + default
        value = await self.cache.get(cache_key)
        if value is None:
            texts = await self.get_by_key(key=key)
            if not texts:
                value = default
            else:
                value = sep.join(texts)
            value = value.replace("<p>", "").replace("</p>", "")
            await self.cache.set(cache_key, value)
        return value
