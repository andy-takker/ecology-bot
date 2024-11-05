import asyncio
import logging

from aiocache import Cache
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.types import ParseMode
from aiogram_dialog import DialogRegistry

from ecology_bot.database.engine import get_async_session_maker
from ecology_bot.presentors.bot.dialogs.main_menu import (
    get_dialog as get_main_menu_dialog,
)
from ecology_bot.presentors.bot.dialogs.organizations.event_register import (
    get_dialog as get_event_register_dialog,
)
from ecology_bot.presentors.bot.dialogs.organizations.organization_menu import (
    get_dialog as get_org_dialog,
)
from ecology_bot.presentors.bot.dialogs.organizations.organization_register import (
    get_dialog as get_org_register_dialog,
)
from ecology_bot.presentors.bot.dialogs.profile.profile_delete import (
    get_dialog as get_delete_profile_dialog,
)
from ecology_bot.presentors.bot.dialogs.profile.profile_menu import (
    get_dialog as get_profile_dialog,
)
from ecology_bot.presentors.bot.dialogs.profile.profile_register import (
    get_dialog as get_profile_register_dialog,
)
from ecology_bot.presentors.bot.dialogs.profile.volunteer_register import (
    get_dialog as get_volunteer_register_dialog,
)
from ecology_bot.presentors.bot.dialogs.states import MainSG
from ecology_bot.presentors.bot.middlewares.database_middleware import (
    DatabaseMiddleware,
)
from ecology_bot.utils.get_settings import get_settings

log = logging.getLogger(__name__)


def register_dialogs(registry: DialogRegistry) -> None:
    log.info("Register dialogs")
    dialogs = [
        get_main_menu_dialog,
        get_profile_register_dialog,
        get_org_register_dialog,
        get_org_dialog,
        get_profile_dialog,
        get_delete_profile_dialog,
        get_volunteer_register_dialog,
        get_event_register_dialog,
    ]
    for dialog in dialogs:
        registry.register(dialog())
    registry.register_start_handler(MainSG.main)


async def start_bot() -> None:
    log.info("Init bot")
    settings = get_settings()
    async_session_maker = get_async_session_maker(
        db_url=settings.SQLALCHEMY_DATABASE_URI
    )
    if settings.DEBUG:
        storage = MemoryStorage()
        cache = Cache(cache_class=Cache.MEMORY)
    else:
        cache = Cache(
            cache_class=Cache.REDIS,
            endpoint=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_CACHE_DB,
        )
        storage = RedisStorage2(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_STORAGE_DB,
        )
        redis = await storage.redis()
        await redis.flushdb()
        log.info("Redis DB was cleared!")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=storage)

    dp.middleware.setup(
        DatabaseMiddleware(
            async_session_maker=async_session_maker,
            cache=cache,
        )
    )

    registry = DialogRegistry(dp)
    register_dialogs(registry=registry)

    try:
        log.info("Start bot")
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
    log.info("Stop bot!")


def main() -> None:
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
