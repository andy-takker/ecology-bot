from sqlalchemy import delete
from sqlalchemy.future import select

from ecology_bot.bot.services.dao.base import DAO
from ecology_bot.database.models import (
    GlobalEvent,
    GlobalEventUser,
    GlobalMailing,
    User,
)


class GlobalEventDAO(DAO):
    async def get_active_global_events(self) -> list[GlobalEvent]:
        q = select(GlobalEvent).where(GlobalEvent.is_active)
        return (await self.session.execute(q)).scalars().all()

    async def get_global_event(self, global_event_id: int) -> GlobalEvent | None:
        return await self.session.get(GlobalEvent, global_event_id)

    async def get_global_event_user(
        self, global_event_id, user_id
    ) -> GlobalEventUser | None:
        q = select(GlobalEventUser).where(
            GlobalEventUser.user_id == user_id,
            GlobalEventUser.global_event_id == global_event_id,
            GlobalEventUser.is_subscribed == True,
        )
        return (await self.session.execute(q)).scalars().first()

    async def create_global_event_user(
        self, user_id: int, global_event_id: int
    ) -> GlobalEventUser:
        global_event_user = GlobalEventUser(
            user_id=user_id,
            global_event_id=global_event_id,
            is_subscribed=True,
        )
        self.session.add(global_event_user)
        await self.session.commit()
        await self.session.refresh(global_event_user)
        return global_event_user

    async def delete_global_event(self, user_id: int, global_event_id: int) -> None:
        q = delete(GlobalEventUser).where(
            GlobalEventUser.user_id == user_id,
            GlobalEventUser.global_event_id == global_event_id,
        )
        await self.session.execute(q)
        await self.session.commit()

    async def get_global_mailing(self, global_mailing_id: int) -> GlobalMailing | None:
        return await self.session.get(GlobalMailing, global_mailing_id)

    async def get_users_by_global_event(self, global_event_id: int) -> list[User]:
        q = (
            select(User)
            .join(GlobalEventUser, GlobalEventUser.user_id == User.id)
            .where(GlobalEventUser.global_event_id == global_event_id)
        )
        return (await self.session.execute(q)).scalars().all()
