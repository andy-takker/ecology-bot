from sqlalchemy import desc
from sqlalchemy.future import select

from ecology_bot.bot.services.dao.base import DAO
from ecology_bot.database.models import TextChunk


class TextChunkDAO(DAO):

    async def get_by_key(self, key: str) -> list[str]:
        q = select(TextChunk.text).where(TextChunk.key == key).order_by(desc(TextChunk.weight))
        return (await self.session.execute(q)).scalars().all()
