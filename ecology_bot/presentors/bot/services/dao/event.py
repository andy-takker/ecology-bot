from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ecology_bot.adapters.database.models import (
    Activity,
    ActivityEvent,
    ActivityProfile,
    Event,
    Profile,
    VolunteerType,
    VolunteerTypeEvent,
    VolunteerTypeProfile,
)
from ecology_bot.presentors.bot.services.dao.base import DAO


class EventDAO(DAO):
    async def create_event(
        self,
        data: dict,
        activities: list[Activity] | None = None,
        volunteer_types: list[VolunteerType] | None = None,
    ) -> Event:
        event = Event()
        event.update(data)
        if activities is not None:
            event.activities = activities
        if volunteer_types is not None:
            event.volunteer_types = volunteer_types
        async with self.session:
            self.session.add(event)
            await self.session.commit()
            await self.session.refresh(event)
            return event

    async def get_event(self, event_id: int) -> Event | None:
        return await self.session.get(
            Event,
            event_id,
            options=(
                selectinload(Event.district),
                selectinload(Event.activities),
                selectinload(Event.volunteer_types),
                selectinload(Event.organization),
            ),
        )

    async def get_profiles_for_event(self, event: Event) -> list[Profile]:
        """Возвращает список профилей для рассылок событий"""

        query = (
            select(Profile)
            .options(selectinload(Profile.user))
            .join(ActivityProfile, Profile.id == ActivityProfile.profile_id)
            .join(
                ActivityEvent, ActivityProfile.activity_id == ActivityEvent.activity_id
            )
            .filter(ActivityEvent.event_id == event.id, event.id == Profile.district_id)
        )
        return (await self.session.execute(query)).scalars().all()

    async def get_profiles_for_recruitment(self, event: Event) -> list[Profile]:
        query = (
            select(Profile)
            .options(selectinload(Profile.user))
            .join(VolunteerTypeProfile, Profile.id == VolunteerTypeProfile.profile_id)
            .join(
                VolunteerTypeEvent,
                VolunteerTypeProfile.volunteer_type_id
                == VolunteerTypeEvent.volunteer_type_id,
            )
            .filter(
                VolunteerTypeEvent.event_id == event.id,
                Profile.is_event_organizer.is_(True),
                Profile.district_id == event.district_id,
            )
        )
        return (await self.session.execute(query)).scalars().all()
