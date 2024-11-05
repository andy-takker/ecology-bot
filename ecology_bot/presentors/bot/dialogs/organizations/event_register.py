from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Data, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Back

from ecology_bot.adapters.database.models import EventType, Organization
from ecology_bot.presentors.bot.dialogs.states import CreateEventSG
from ecology_bot.presentors.bot.services.repo import Repo
from ecology_bot.presentors.bot.windows.activity_window import ActivityWindow
from ecology_bot.presentors.bot.windows.confirm_window import ConfirmWindow
from ecology_bot.presentors.bot.windows.district_window import DistrictWindow
from ecology_bot.presentors.bot.windows.event_type_window import EventTypeWindow
from ecology_bot.presentors.bot.windows.input_text_window import InputTextWindow
from ecology_bot.presentors.bot.windows.volunteer_type_window import VolunteerTypeWindow
from ecology_bot.workers.mailing import execute_mailing


async def get_name_prev_state(c: CallbackQuery, widget: Any, manager: DialogManager):
    if (
        EventType(manager.current_context().dialog_data["event_type"])
        == EventType.DEFAULT
    ):
        return CreateEventSG.activity
    else:
        return CreateEventSG.volunteer_type


async def get_desc_prev_state(c: CallbackQuery, widget: Any, manager: DialogManager):
    return CreateEventSG.name


async def on_start(data: Data, manager: DialogManager):
    organization_id: Organization = data["organization_id"]
    repo: Repo = manager.data["repo"]
    organization = await repo.organization_dao.get_organization(organization_id)
    region_id = (
        await repo.district_dao.get_district(district_id=organization.district_id)
    ).region_id
    manager.current_context().dialog_data["organization_id"] = organization.id
    manager.current_context().dialog_data["region_id"] = region_id


async def on_finish(c: CallbackQuery, widget: Any, manager: DialogManager):
    repo: Repo = manager.data["repo"]
    data = manager.current_context().dialog_data
    activities = None
    if EventType(data["event_type"]) == EventType.DEFAULT:
        activities = await repo.activity_dao.get_activities(ids=data["activity"])
    volunteer_types = None
    if EventType(data["event_type"]) == EventType.RECRUITMENT:
        volunteer_types = await repo.volunteer_type_dao.get_volunteer_types(
            ids=data["volunteer_type"]
        )
    event = await repo.event_dao.create_event(
        data={
            "organization_id": data["organization_id"],
            "district_id": data["district_id"],
            "type": data["event_type"],
            "name": data["name"],
            "description": data["description"],
        },
        activities=activities,
        volunteer_types=volunteer_types,
    )
    execute_mailing.delay(event.id)
    await c.message.answer(f'Событие "{data["name"]}" создано! ')
    manager.show_mode = ShowMode.SEND
    await manager.done()
    manager.show_mode = ShowMode.EDIT


async def get_name_text(dialog_manager: DialogManager, **kwargs):
    event_type = dialog_manager.current_context().dialog_data["event_type"]
    if EventType(event_type) == EventType.DEFAULT:
        return {
            "text": "Введите название события:",
        }
    else:
        return {
            "text": "Введите название вакансии волонтера:",
        }


async def get_description_text(dialog_manager: DialogManager, **kwargs):
    event_type = dialog_manager.current_context().dialog_data["event_type"]
    if EventType(event_type) == EventType.DEFAULT:
        return {
            "text": "Введите описание события:",
        }
    else:
        return {
            "text": "Введите описание вакансии:",
        }


def get_dialog():
    district_window = DistrictWindow(state=CreateEventSG.district, is_cancel=True)
    event_type_window = EventTypeWindow(
        state=CreateEventSG.event_type,
        event_type_states={
            EventType.DEFAULT: CreateEventSG.activity,
            EventType.RECRUITMENT: CreateEventSG.volunteer_type,
        },
    )
    activity_window = ActivityWindow(
        state=CreateEventSG.activity,
        prev=Back,
        all=False,
        prev_state=CreateEventSG.event_type,
    )
    volunteer_type_window = VolunteerTypeWindow(
        state=CreateEventSG.volunteer_type,
        prev_state=CreateEventSG.event_type,
        next_state=CreateEventSG.name,
    )
    name_window = InputTextWindow(
        getter_text=get_name_text,
        state=CreateEventSG.name,
        id="name",
        get_prev_state=get_name_prev_state,
    )
    description_window = InputTextWindow(
        getter_text=get_description_text,
        state=CreateEventSG.description,
        id="description",
        get_prev_state=get_desc_prev_state,
    )
    confirm_window = ConfirmWindow(
        state=CreateEventSG.confirm,
        text="Вы действительно хотите создать рассылку?",
        on_confirm=on_finish,
    )
    return Dialog(
        district_window,
        event_type_window,
        volunteer_type_window,
        activity_window,
        name_window,
        description_window,
        confirm_window,
        on_start=on_start,
    )
