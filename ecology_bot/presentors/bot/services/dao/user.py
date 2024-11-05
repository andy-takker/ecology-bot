from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ecology_bot.adapters.database.models import (
    Activity,
    ActivityEvent,
    ActivityOrganization,
    ActivityProfile,
    Event,
    Organization,
    Profile,
    User,
    VolunteerType,
    VolunteerTypeEvent,
    VolunteerTypeProfile,
)
from ecology_bot.presentors.bot.services.dao.base import DAO


class UserDAO(DAO):
    async def get_user(self, telegram_id: int) -> User | None:
        q = (
            select(User)
            .filter_by(telegram_id=telegram_id)
            .options(
                selectinload(User.organizations),
                selectinload(User.profile).selectinload(Profile.activities),
            )
        )
        return (await self.session.execute(q)).scalar()

    async def create_user(self, telegram_id: int, is_admin: bool = False) -> User:
        async with self.session:
            user = User(telegram_id=telegram_id, is_admin=is_admin)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def create_user_if_not_exist(
        self, telegram_id: int, is_admin: bool = False
    ) -> User:
        user = await self.get_user(telegram_id=telegram_id)
        if user is None:
            return await self.create_user(telegram_id=telegram_id, is_admin=is_admin)
        return user

    async def get_user_checked_organization(
        self, telegram_id: int
    ) -> list[Organization]:
        q = (
            select(Organization)
            .join(User)
            .filter(
                User.telegram_id == telegram_id,
                Organization.is_checked,
            )
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_profile(self, telegram_id: int) -> Profile | None:
        q = Profile.q_from_telegram_id(telegram_id).options(
            selectinload(Profile.district),
            selectinload(Profile.region),
            selectinload(Profile.activities),
            selectinload(Profile.volunteer_types),
        )
        return (await self.session.execute(q)).scalars().first()

    async def create_profile(
        self, user: User, region_id: int, district_id: int, activities: list[Activity]
    ) -> Profile:
        async with self.session:
            profile = Profile()
            profile.user = user
            profile.region_id = region_id
            profile.district_id = district_id
            profile.activities = activities
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile

    async def update_profile(
        self,
        telegram_id: int,
        data: dict,
        volunteer_types: list[VolunteerType] | None = None,
        activities: list[Activity] | None = None,
    ):
        q = Profile.q_from_telegram_id(telegram_id).options(
            selectinload(Profile.activities),
            selectinload(Profile.volunteer_types),
        )
        async with self.session:
            profile = (await self.session.execute(q)).scalars().first()
            if profile is None:
                return
            profile.update(data=data)
            if volunteer_types is not None:
                profile.volunteer_types = volunteer_types
            if activities is not None:
                profile.activities = activities
            await self.session.commit()

    async def delete_profile(self, telegram_id: int) -> None:
        async with self.session:
            user = await self.get_user(telegram_id)
            await self.session.execute(
                delete(Profile).where(Profile.user_id == user.id)
            )
            await self.session.commit()

    async def get_events_for_profile(self, profile: Profile) -> list[Event]:
        q = (
            Event.query()
            .join(ActivityEvent, Event.id == ActivityEvent.event_id)
            .join(
                ActivityProfile,
                ActivityEvent.activity_id == ActivityProfile.activity_id,
            )
            .filter(
                ActivityProfile.profile_id == profile.id,
                Event.district_id == profile.district_id,
            )
        )
        events = (await self.session.execute(q)).scalars().all()
        if profile.is_event_organizer:
            q = (
                Event.query()
                .join(VolunteerTypeEvent, VolunteerTypeEvent.event_id == Event.id)
                .join(
                    VolunteerTypeProfile,
                    VolunteerTypeEvent.volunteer_type_id
                    == VolunteerTypeProfile.volunteer_type_id,
                )
                .filter(
                    VolunteerTypeProfile.profile_id == profile.id,
                    Profile.district_id == Event.district_id,
                )
            )
            result = (await self.session.execute(q)).scalars().all()
            events.extend(result)
        return events

    async def get_organizations_by_profile(
        self, profile: Profile, activity_id: int
    ) -> list[Organization]:
        q = (
            Organization.query()
            .join(
                ActivityOrganization,
                Organization.id == ActivityOrganization.organization_id,
            )
            .filter(
                ActivityOrganization.activity_id == activity_id,
                profile.district_id == Organization.district_id,
            )
        )
        return (await self.session.execute(q)).scalars().all()

    async def get_admins(self) -> list[User]:
        q = select(User).filter_by(is_admin=True)
        return (await self.session.execute(q)).scalars().all()
