from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Multiselect,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.presentors.bot.dialogs.states import RegisterVolunteerSG
from ecology_bot.presentors.bot.services.repo import Repo


async def name_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await dialog.next(manager)


def get_name_window() -> Window:
    return Window(
        Const("Напиши свое имя и фамилию"),
        Cancel(text=Const("Назад"), result={}),
        MessageInput(name_handler),
        state=RegisterVolunteerSG.name,
    )


async def age_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["age"] = m.text
    await dialog.next(manager)


def get_age_window() -> Window:
    return Window(
        Const("Сколько тебе лет?"),
        Back(text=Const("Назад")),
        MessageInput(age_handler),
        state=RegisterVolunteerSG.age,
    )


async def get_volunteer_type_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: Repo = dialog_manager.data["repo"]
    return {"volunteer_types": await repo.volunteer_type_dao.get_volunteer_types()}


def get_volunteer_type_keyboard() -> ScrollingGroup:
    volunteer_types = Multiselect(
        Format("\U00002705 {item.name}"),
        Format("{item.name}"),
        id="m_volunteer_types",
        item_id_getter=lambda x: x.id,
        items="volunteer_types",
    )
    return ScrollingGroup(
        volunteer_types,
        id="volunteer_types",
        width=1,
        height=10,
    )


def get_age(text: str):
    try:
        return int(text)
    except ValueError:
        return None


async def complete_volunteer_registration(
    c: CallbackQuery, widget: Any, manager: DialogManager
):
    repo: Repo = manager.data["repo"]
    volunteer_type_widget = manager.dialog().find("m_volunteer_types")
    volunteer_type_ids = list(map(int, volunteer_type_widget.get_checked()))
    volunteer_types = await repo.volunteer_type_dao.get_volunteer_types(
        volunteer_type_ids
    )
    await repo.user_dao.update_profile(
        telegram_id=c.from_user.id,
        data={
            "age": get_age(manager.current_context().dialog_data["age"]),
            "name": manager.current_context().dialog_data["name"],
            "is_event_organizer": True,
        },
        volunteer_types=volunteer_types,
    )
    await c.message.answer(
        "Теперь тебе будут приходить уведомления об "
        "организации волонтерских мероприятий!"
    )
    manager.show_mode = ShowMode.SEND
    await manager.done({})
    manager.show_mode = ShowMode.EDIT


def get_volunteer_type_window() -> Window:
    volunteer_types = get_volunteer_type_keyboard()

    return Window(
        Const("Какие типы волонтерств тебе нравятся?"),
        volunteer_types,
        Button(
            text=Const(
                "Завершить регистрацию",
            ),
            id="finish_profile",
            on_click=complete_volunteer_registration,
        ),
        Back(text=Const("Назад")),
        getter=get_volunteer_type_data,
        state=RegisterVolunteerSG.volunteer_type,
    )


def get_dialog() -> Dialog:
    name_window = get_name_window()
    age_window = get_age_window()
    volunteer_type_window = get_volunteer_type_window()
    return Dialog(name_window, age_window, volunteer_type_window)
