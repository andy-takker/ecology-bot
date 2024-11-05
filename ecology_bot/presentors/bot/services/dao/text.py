from sqlalchemy import desc
from sqlalchemy.future import select

from ecology_bot.adapters.database.models import TextChunk
from ecology_bot.presentors.bot.services.dao.base import DAO


class TextChunkDAO(DAO):
    async def get_by_key(self, key: str) -> list[str]:
        q = (
            select(TextChunk.text)
            .where(TextChunk.key == key)
            .order_by(desc(TextChunk.weight))
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_text(self, key: str, sep: str = "\n", default: str = "") -> str:
        cache_key = "text_chunk:" + key
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
