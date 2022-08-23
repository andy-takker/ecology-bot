from typing import Optional

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ecology_bot.database import District, Activity, Organization, User, Event
from ecology_bot.bot.services.dao.base import DAO


class OrganizationDAO(DAO):
    async def create_organization(
            self,
            creator_id: int,
            name: str,
            district_id: int,
            activities: list[Activity],
    ) -> Organization:
        async with self.session:
            organization = Organization(
                creator_id=creator_id,
                name=name,
                activities=activities,
                district_id=district_id,
            )
            self.session.add(organization)
            await self.session.commit()
            await self.session.refresh(organization)
            return organization

    async def get_organization(self, organization_id: int) -> Optional[Organization]:
        return await self.session.get(
            Organization,
            organization_id,
            options=(
                selectinload(Organization.creator),
                selectinload(Organization.district),
                selectinload(Organization.activities),
            ),
        )

    async def get_events_by_organization(self, organization_id: int) -> list[Event]:
        q = Event.query().where(Event.organization_id == organization_id)
        return (await self.session.execute(q)).scalars().all()

    async def get_unchecked_organizations(self, user_id: int = None) -> list[Organization]:
        q = select(Organization).where(Organization.is_checked == False)
        if user_id is not None:
            q.where(Organization.creator_id == user_id)
        return (await self.session.execute(q)).scalars().all()

    async def update_organization(self, organization_id: int, data: dict):
        async with self.session:
            org = await self.get_organization(organization_id)
            org.update(data)
            await self.session.commit()

    async def get_organizations_by_creator(self, telegram_id: int, is_checked: bool | None = None) -> list[
        Organization]:
        q = select(Organization).join(User, Organization.creator_id == User.id).where(User.telegram_id == telegram_id)
        if is_checked is not None:
            q = q.where(Organization.is_checked == is_checked)
        return (await self.session.execute(q)).scalars().all()
