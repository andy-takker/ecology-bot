from typing import Any, Type

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Multiselect, Next, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const

from ecology_bot.bot.services.repo import Repo
from ecology_bot.bot.utils.switch_to_button import GoTo


async def get_org_activity_data(dialog_manager: DialogManager, **kwargs) -> dict:
    organization_id = dialog_manager.current_context().dialog_data["organization_id"]
    repo: Repo = dialog_manager.data["repo"]
    organization = await repo.organization_dao.get_organization(organization_id)
    return {
        "activities": organization.activities,
    }


async def get_activity_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: Repo = dialog_manager.data["repo"]
    activities = await repo.activity_dao.get_activities()
    return {
        "activities": activities,
    }


async def on_activity_selected(
    c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    manager.current_context().dialog_data["activity_id"] = int(item_id)
    await manager.dialog().next()


async def save_activity(c: CallbackQuery, widget: Any, manager: DialogManager):
    activities_widget = manager.dialog().find("m_activities")
    activity_ids = list(map(int, activities_widget.get_checked()))
    manager.current_context().dialog_data["activity"] = activity_ids


class ActivityWindow(Window):
    def __init__(
        self,
        state: State,
        prev: Type[Back | Cancel] = Cancel,
        all=True,
        prev_state: None | State = None,
    ):
        message = Const("Выберите активности")
        activities = self.get_activity_keyboard()
        getter = get_activity_data if all else get_org_activity_data
        if not prev_state:
            back = prev(text=Const("Назад"))
        else:
            back = GoTo(text="Назад", id="switch_to_back", state=prev_state)
        super().__init__(
            message,
            activities,
            Next(text=Const("Далее"), on_click=save_activity),
            back,
            getter=getter,
            state=state,
        )

    def get_activity_keyboard(self) -> ScrollingGroup:
        el_id = "m_activities"
        getter = lambda x: x.id
        items = "activities"
        activities = Multiselect(
            Format("\U00002705 {item.name}"),
            Format("{item.name}"),
            id=el_id,
            item_id_getter=getter,
            items=items,
        )
        sg = ScrollingGroup(
            activities,
            id="activities",
            width=1,
            height=10,
        )
        return sg
