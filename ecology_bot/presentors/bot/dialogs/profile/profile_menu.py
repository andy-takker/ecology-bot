from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Column, Select, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.presentors.bot.dialogs.states import (
    ProfileDeleteSG,
    ProfileManagementSG,
    RegisterVolunteerSG,
)
from ecology_bot.presentors.bot.services.repo import Repo


async def show_organization_by_activity(
    c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    repo: Repo = manager.data["repo"]
    organizations = await repo.user_dao.get_organizations_by_profile(
        profile=await repo.user_dao.get_profile(telegram_id=c.from_user.id),
        activity_id=int(item_id),
    )
    msg = []
    if organizations:
        msg.append("В твоем районе с такой активностью есть вот эти организации:")
        for org in organizations:
            msg.append(org.info)
    else:
        msg.append(
            "В Вашем районе не зарегистрированы экологические организации с "
            "таким направлением. Возможно, они появятся позже, а пока можете "
            "выбрать другой район или направление"
        )
    manager.current_context().dialog_data["activity_info"] = "\n\n".join(msg)
    await manager.dialog().switch_to(ProfileManagementSG.activity_info)


async def activity_info_data(dialog_manager: DialogManager, **kwargs):
    return {
        "activity_info": dialog_manager.current_context().dialog_data["activity_info"]
    }


def get_profile_activities():
    activities = Select(
        Format("{item.name}"),
        id="s_activities",
        item_id_getter=lambda x: x.id,
        items="activities",
        on_click=show_organization_by_activity,
    )
    return Column(activities)


async def profile_window_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    profile = await repo.user_dao.get_profile(
        telegram_id=dialog_manager.event.from_user.id
    )
    return {
        "activities": profile.activities,
    }


async def profile_info_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    profile = await repo.user_dao.get_profile(
        telegram_id=dialog_manager.event.from_user.id
    )
    return {
        "profile_info": profile.info,
    }


def is_event_organizer(data: dict, whenable: Any, manager: DialogManager):
    return data["dialog_data"].get("is_event_organizer", False)


def get_menu_window() -> Window:
    activities = get_profile_activities()
    return Window(
        Const("Меню волонтера"),
        activities,
        SwitchTo(
            id="switch_to_profile_info",
            state=ProfileManagementSG.profile_info,
            text=Const("Инфо профиля"),
        ),
        SwitchTo(
            id="switch_to_events_info",
            state=ProfileManagementSG.events_info,
            text=Const("Показать подходящие события"),
        ),
        Start(
            id="create_volunteer",
            state=RegisterVolunteerSG.name,
            text=Const("Хочу помочь организовать экособытие"),
            when=lambda d, w, m: not is_event_organizer(d, w, m),
        ),
        Start(
            id="delete_profile",
            state=ProfileDeleteSG.confirm,
            text=Const("Удалить профиль"),
        ),
        Cancel(text=Const("Назад")),
        getter=profile_window_data,
        state=ProfileManagementSG.main,
    )


def get_activity_info_window() -> Window:
    return Window(
        Format("{activity_info}"),
        SwitchTo(
            id="switch_to_main",
            state=ProfileManagementSG.main,
            text=Const("Назад"),
        ),
        state=ProfileManagementSG.activity_info,
        getter=activity_info_data,
    )


def get_profile_info_window() -> Window:
    return Window(
        Format("{profile_info}"),
        SwitchTo(
            id="switch_to_main",
            state=ProfileManagementSG.main,
            text=Const("Назад"),
        ),
        state=ProfileManagementSG.profile_info,
        getter=profile_info_data,
    )


async def events_info_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    telegram_id = dialog_manager.event.from_user.id
    events = await repo.user_dao.get_events_for_profile(
        profile=await repo.user_dao.get_profile(telegram_id=telegram_id)
    )
    msgs = []
    for e in events:
        msgs.append(e.message)
    msgs.append(f"Под твой профиль подходит {len(events)} мероприятий.")
    return {"events_info": "\n-------\n".join(msgs)}


def get_events_info_window() -> Window:
    return Window(
        Format("{events_info}"),
        SwitchTo(
            id="switch_to_main",
            state=ProfileManagementSG.main,
            text=Const("Назад"),
        ),
        state=ProfileManagementSG.events_info,
        getter=events_info_data,
    )


async def on_process_result(data: Data, result: dict, manager: DialogManager):
    await on_start(data, manager)
    if result.get("action", None) == "delete_profile":
        repo: Repo = manager.data["repo"]
        await repo.user_dao.delete_profile(telegram_id=manager.event.from_user.id)
        await manager.done()


async def on_start(self, manager: DialogManager):
    user_id = manager.event.from_user.id
    repo: Repo = manager.data["repo"]
    profile = await repo.user_dao.get_profile(telegram_id=user_id)
    dialog_data = manager.current_context().dialog_data
    dialog_data["is_event_organizer"] = profile.is_event_organizer


def get_dialog() -> Dialog:
    menu_window = get_menu_window()
    activity_window = get_activity_info_window()
    profile_info_window = get_profile_info_window()
    events_info_window = get_events_info_window()
    return Dialog(
        menu_window,
        activity_window,
        profile_info_window,
        events_info_window,
        on_process_result=on_process_result,
        on_start=on_start,
    )
