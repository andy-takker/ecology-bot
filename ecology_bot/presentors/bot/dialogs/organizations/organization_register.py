from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
)
from aiogram_dialog.widgets.text import Const

from ecology_bot.presentors.bot.dialogs.messages import (
    DEFAULT_MESSAGES,
    ON_ORG_REGISTRATION_END_TEXT,
)
from ecology_bot.presentors.bot.dialogs.profile.profile_register import (
    get_not_region_text,
    input_handler,
)
from ecology_bot.presentors.bot.dialogs.states import RegisterOrganizationSG
from ecology_bot.presentors.bot.services.repo import Repo
from ecology_bot.presentors.bot.windows.activity_window import ActivityWindow
from ecology_bot.presentors.bot.windows.confirm_window import ConfirmWindow
from ecology_bot.presentors.bot.windows.district_window import DistrictWindow
from ecology_bot.presentors.bot.windows.input_text_window import InputTextWindow
from ecology_bot.presentors.bot.windows.region_window import RegionWindow


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next(manager)


def get_name_window():
    return Window(
        Const("Введите название организации"),
        Back(text=Const("Назад")),
        MessageInput(name_handler),
        state=RegisterOrganizationSG.name,
    )


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    data = manager.current_context().dialog_data
    repo: Repo = manager.data["repo"]
    user = await repo.user_dao.get_user(telegram_id=c.from_user.id)
    await repo.organization_dao.create_organization(
        district_id=data["district_id"],
        creator_id=user.id,
        activities=await repo.activity_dao.get_activities(ids=data["activity"]),
        name=data["name"],
    )

    await c.message.answer(
        await repo.text_chunk_dao.get_text(
            key=ON_ORG_REGISTRATION_END_TEXT,
            default=DEFAULT_MESSAGES[ON_ORG_REGISTRATION_END_TEXT],
        )
    )
    manager.show_mode = ShowMode.SEND
    await manager.done()
    manager.show_mode = ShowMode.EDIT


async def confirm_data(dialog_manager: DialogManager, **kwargs) -> dict:
    return {
        "name": dialog_manager.current_context().dialog_data["name"],
    }


async def get_not_region_prev_state(
    c: CallbackQuery, widget: Any, manager: DialogManager
):
    return RegisterOrganizationSG.region


def get_dialog() -> Dialog:
    activity_window = ActivityWindow(state=RegisterOrganizationSG.activity)
    region_window = RegionWindow(
        state=RegisterOrganizationSG.region,
        not_region_state=RegisterOrganizationSG.not_region,
        next_state=RegisterOrganizationSG.district,
    )
    not_region_window = InputTextWindow(
        id="new_region",
        getter_text=get_not_region_text,
        state=RegisterOrganizationSG.not_region,
        get_prev_state=get_not_region_prev_state,
        handler=input_handler,
    )
    district_window = DistrictWindow(
        state=RegisterOrganizationSG.district, prev_state=RegisterOrganizationSG.region
    )
    name_window = get_name_window()
    confirm_window = ConfirmWindow(
        text='Зарегистрировать организацию "{name}"?',
        state=RegisterOrganizationSG.confirm,
        getter=confirm_data,
        on_confirm=on_finish,
    )
    dialog = Dialog(
        activity_window,
        region_window,
        not_region_window,
        district_window,
        name_window,
        confirm_window,
    )
    return dialog
