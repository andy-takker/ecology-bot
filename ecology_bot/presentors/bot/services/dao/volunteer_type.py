from sqlalchemy.future import select

from ecology_bot.adapters.database.models import VolunteerType
from ecology_bot.presentors.bot.services.dao.base import DAO


class VolunteerTypeDAO(DAO):
    async def get_volunteer_types(
        self, ids: list[int] | None = None
    ) -> list[VolunteerType]:
        q = select(VolunteerType)
        if ids is not None:
            q = q.filter(VolunteerType.id.in_(ids))
        return (await self.session.execute(q)).scalars().all()
