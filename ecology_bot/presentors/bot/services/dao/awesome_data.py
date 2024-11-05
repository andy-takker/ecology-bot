from ecology_bot.adapters.database.models import AwesomeData
from ecology_bot.presentors.bot.services.dao.base import DAO


class AwesomeDataDAO(DAO):
    async def save_data(
        self, data: str, description: str, from_user_id: None | int = None
    ) -> None:
        async with self.session:
            awesome_data = AwesomeData(
                from_user_id=from_user_id,
                description=description,
                data=data,
            )
            self.session.add(awesome_data)
            await self.session.commit()
