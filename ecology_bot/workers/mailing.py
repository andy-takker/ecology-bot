import asyncio

from aiogram import Bot, types

from ecology_bot.database.models import GlobalMailing
from ecology_bot.utils.get_settings import get_settings

from ecology_bot.database import EventType, User
from ecology_bot.database.engine import get_async_session_maker
from ecology_bot.bot.services.repo import Repo
from ecology_bot.workers.celery import celery


@celery.task(name="execute_mailing", bind=True, track_started=True)
def execute_mailing(self, event_id: int) -> None:
    asyncio.run(_execute_mailing(event_id))


async def _execute_mailing(event_id: int) -> None:
    """Выполняет рассылку по волонтерам"""
    settings = get_settings()
    AsyncSession = get_async_session_maker(db_url=settings.SQLALCHEMY_DATABASE_URI)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    session = AsyncSession()
    repo = Repo(session=session, cache=None)
    event = await repo.event_dao.get_event(event_id)
    if event.type == EventType.DEFAULT:
        profiles = await repo.event_dao.get_profiles_for_event(event=event)

    else:
        profiles = await repo.event_dao.get_profiles_for_recruitment(event=event)
    for profile in profiles:
        await bot.send_message(
            chat_id=profile.user.telegram_id,
            text=event.message,
            parse_mode=types.ParseMode.MARKDOWN,
        )
    await bot.close()


@celery.task(name="execute_global_mailing", bind=True, track_started=True)
def execute_global_mailing(self, global_mailing_id: int) -> None:
    asyncio.run(_execute_global_mailing(global_mailing_id))


async def _execute_global_mailing(global_mailing_id: int) -> None:
    """Выполняет рассылку по глобальным событиям"""
    settings = get_settings()
    AsyncSession = get_async_session_maker(db_url=settings.SQLALCHEMY_DATABASE_URI)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    session = AsyncSession()
    repo = Repo(session=session, cache=None)

    global_mailing: GlobalMailing = await repo.global_event_dao.get_global_mailing(
        global_mailing_id
    )

    users: list[User] = await repo.global_event_dao.get_users_by_global_event(
        global_mailing.global_event_id
    )
    for user in users:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=global_mailing.name + "\n" + global_mailing.clean_description,
            parse_mode=types.ParseMode.HTML,
        )
    await bot.close()
