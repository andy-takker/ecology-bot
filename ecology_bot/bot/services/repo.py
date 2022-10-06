from aiocache import Cache
from sqlalchemy.ext.asyncio import AsyncSession

from ecology_bot.bot.services.dao import (
    ActivityDAO,
    RegionDAO,
    DistrictDAO,
    OrganizationDAO,
    UserDAO,
    VolunteerTypeDAO,
    EventDAO,
    TextChunkDAO,
    AwesomeDataDAO,
)


class Repo:
    def __init__(self, session: AsyncSession, cache: Cache):
        self.session = session
        self.event_dao = EventDAO(session=session)
        self.region_dao = RegionDAO(session=session)
        self.district_dao = DistrictDAO(session=session)
        self.activity_dao = ActivityDAO(session=session)
        self.organization_dao = OrganizationDAO(session=session)
        self.user_dao = UserDAO(session=session)
        self.volunteer_type_dao = VolunteerTypeDAO(session=session)
        self.text_chunk_dao = TextChunkDAO(session=session, cache=cache)
        self.awesome_data_dao = AwesomeDataDAO(session=session)
