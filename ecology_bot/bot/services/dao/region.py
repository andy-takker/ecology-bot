from sqlalchemy.future import select

from ecology_bot.database import Region
from ecology_bot.bot.services.dao.base import DAO


class RegionDAO(DAO):
    """Data class for regions"""

    async def get_regions(self, ids: list[int] | None = None) -> list[Region]:
        async with self.session:
            q = select(Region)
            if ids is not None:
                q.filter(Region.id.in_(ids))
            return (await self.session.execute(q)).scalars().all()
