from sqlalchemy.future import select

from ecology_bot.adapters.database.models import District
from ecology_bot.presentors.bot.services.dao.base import DAO


class DistrictDAO(DAO):
    async def get_districts(self, ids: list[int] | None = None) -> list[District]:
        q = select(District)
        if ids is not None:
            q = q.filter(District.id.in_(ids))
        return (await self.session.execute(q)).scalars().all()

    async def get_districts_by_region(
        self, region_id: int, parent_id: int | None
    ) -> list[District]:
        """Возвращает список районов по региону"""
        q = select(District).where(
            District.region_id == region_id, District.parent_id == parent_id
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_children(self, district_id: int) -> list[District]:
        """Возвращает дочерние регионы"""
        q = select(District).where(District.parent_id == district_id)
        return (await self.session.execute(q)).scalars().all()

    async def get_district(self, district_id: int) -> District | None:
        return await self.session.get(District, district_id)
