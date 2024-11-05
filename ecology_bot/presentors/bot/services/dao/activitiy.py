from sqlalchemy.future import select

from ecology_bot.adapters.database.models import Activity
from ecology_bot.presentors.bot.services.dao.base import DAO


class ActivityDAO(DAO):
    async def get_activities(self, ids: list[int] | None = None):
        q = select(Activity)
        if ids is not None:
            q = q.filter(Activity.id.in_(ids))
        return (await self.session.execute(q)).scalars().all()
