from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.presentors.bot.dialogs.states import (
    CreateEventSG,
    OrganizationManagementSG,
)
from ecology_bot.presentors.bot.services.repo import Repo
from ecology_bot.presentors.bot.utils.start_button import StartBtn


async def get_org_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    organization_id = dialog_manager.current_context().dialog_data["organization_id"]
    organization = await repo.organization_dao.get_organization(organization_id)
    return {"org": organization}


async def on_create_event(c: CallbackQuery, widget: Any, manager: DialogManager):
    org_id = manager.current_context().dialog_data["organization_id"]
    return {
        "organization_id": org_id,
    }


def get_menu_window() -> Window:
    return Window(
        Format('Вы в меню организации "{org.name}".'),
        StartBtn(
            id="create_event",
            state=CreateEventSG.district,
            text=Const("Создать событие"),
            getter=on_create_event,
        ),
        SwitchTo(
            id="events_info",
            state=OrganizationManagementSG.event_list,
            text=Const("События организации"),
        ),
        SwitchTo(
            id="switch_to_chat",
            state=OrganizationManagementSG.chat,
            text=Const("Вступить в чат по вашему району"),
        ),
        Cancel(text=Const("Назад к списку организаций")),
        state=OrganizationManagementSG.menu,
        getter=get_org_data,
    )


async def get_chat_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    org_id = dialog_manager.current_context().dialog_data["organization_id"]
    org = await repo.organization_dao.get_organization(org_id)
    district = await repo.district_dao.get_district(org.district_id)
    return {
        "chat_link": district.invite_link,
    }


def get_chat_window():
    return Window(
        Format("Ссылка на чат вашего района: {chat_link}"),
        SwitchTo(
            id="switch_to_menu",
            state=OrganizationManagementSG.menu,
            text=Const("Назад"),
        ),
        state=OrganizationManagementSG.chat,
        getter=get_chat_data,
    )


async def events_info_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    org_id = dialog_manager.current_context().dialog_data["organization_id"]
    events = await repo.organization_dao.get_events_by_organization(org_id)
    msgs = []
    for e in events:
        msgs.append(e.message)
    msgs.append(f"У вас было <b>{len(events)}</b> событий.")
    return {"events_info": "\n------\n".join(msgs)}


def get_event_info_window() -> Window:
    return Window(
        Format("{events_info}"),
        SwitchTo(
            id="switch_to_main",
            state=OrganizationManagementSG.menu,
            text=Const("Назад"),
        ),
        state=OrganizationManagementSG.event_list,
        getter=events_info_data,
    )


async def on_start(data: Any, manager: DialogManager):
    manager.current_context().dialog_data = data


def get_dialog() -> Dialog:
    menu_window = get_menu_window()
    chat_window = get_chat_window()
    event_list_window = get_event_info_window()
    return Dialog(
        menu_window,
        chat_window,
        event_list_window,
        on_start=on_start,
    )
