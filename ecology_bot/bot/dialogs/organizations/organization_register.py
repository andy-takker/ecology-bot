from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, ScrollingGroup, Multiselect, Cancel, Next, Select, Row
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.bot.dialogs.states import RegisterOrganizationSG
from ecology_bot.bot.services.repo import Repo
from ecology_bot.bot.windows.activity_window import ActivityWindow
from ecology_bot.bot.windows.confirm_window import ConfirmWindow
from ecology_bot.bot.windows.district_window import DistrictWindow
from ecology_bot.bot.windows.region_window import RegionWindow


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next(manager)


def get_name_window():
    return Window(
        Const('Введите название организации'),
        Back(text=Const('Назад')),
        MessageInput(name_handler),
        state=RegisterOrganizationSG.name,
    )


async def on_finish(c: CallbackQuery, button: Button, manager: DialogManager):
    data = manager.current_context().dialog_data
    repo: Repo = manager.data['repo']
    user = await repo.user_dao.get_user(telegram_id=c.from_user.id)
    await repo.organization_dao.create_organization(
        district_id=data['district_id'],
        creator_id=user.id,
        activities=await repo.activity_dao.get_activities(ids=data['activity']),
        name=data['name'],
    )
    await c.message.answer('Организация создана и отправлена на модерацию! '
                           'Когда мы ее проверим, Вы получите уведомление.')
    manager.show_mode = ShowMode.SEND
    await manager.done()
    manager.show_mode = ShowMode.EDIT


async def confirm_data(dialog_manager: DialogManager, **kwargs) -> dict:
    return {
        "name": dialog_manager.current_context().dialog_data['name'],
    }


def get_dialog() -> Dialog:
    activity_window = ActivityWindow(state=RegisterOrganizationSG.activity)
    region_window = RegionWindow(state=RegisterOrganizationSG.region,
                                 not_region_state=RegisterOrganizationSG.not_region)
    district_window = DistrictWindow(state=RegisterOrganizationSG.district)
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
        district_window,
        name_window,
        confirm_window,
    )
    return dialog
