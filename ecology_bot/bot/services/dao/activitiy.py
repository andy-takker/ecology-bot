from sqlalchemy.future import select
from typing import Optional

from ecology_bot.database import Activity
from ecology_bot.bot.services.dao.base import DAO


class ActivityDAO(DAO):
    async def get_activities(self, ids: Optional[list[int]] = None):
        q = select(Activity)
        if ids is not None:
            q = q.filter(Activity.id.in_(ids))
        return (await self.session.execute(q)).scalars().all()
