from typing import Type, Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Back, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.bot.services.repo import Repo
from ecology_bot.bot.utils.switch_to_button import GoTo

DISTRICT_MESSAGE = "Выберите населенный пункт"


async def on_district_selected(
    c: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    district_id = int(item_id)
    repo: Repo = dialog_manager.data["repo"]
    children = await repo.district_dao.get_children(district_id=district_id)
    if children:
        dialog_manager.current_context().dialog_data["parent_id"] = district_id
    else:
        dialog_manager.current_context().dialog_data["district_id"] = district_id
        await dialog_manager.dialog().next()


async def get_district_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: Repo = dialog_manager.data["repo"]
    region_id = dialog_manager.current_context().dialog_data["region_id"]
    parent_id = dialog_manager.current_context().dialog_data.get("parent_id")
    districts = await repo.district_dao.get_districts_by_region(
        region_id=region_id, parent_id=parent_id
    )
    return {
        "districts": districts,
    }


class DistrictWindow(Window):
    def __init__(self, state: State, is_cancel: bool = False, prev_state: State = None):
        prev = None
        if is_cancel:
            prev = Cancel(text=Const("Назад"))
        if prev_state is not None:
            prev = GoTo(text="Назад", id="back_to_region", state=prev_state)
        assert prev is not None
        districts = self.get_district_keyboard()
        super().__init__(
            Const(DISTRICT_MESSAGE),
            districts,
            prev,
            getter=get_district_data,
            state=state,
        )

    @staticmethod
    def get_district_keyboard() -> ScrollingGroup:
        districts = Select(
            Format("{item.name}"),
            id="s_districts",
            item_id_getter=lambda x: x.id,
            items="districts",
            on_click=on_district_selected,
        )
        sg = ScrollingGroup(
            districts,
            id="districts",
            width=1,
            height=10,
        )
        return sg
