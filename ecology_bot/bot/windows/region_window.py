from typing import Type, Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Back, Cancel, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.bot.services.repo import Repo


def get_region_keyboard() -> ScrollingGroup:
    regions = Select(
        Format("{item.name}"),
        id="s_regions",
        item_id_getter=lambda x: x.id,
        items="regions",
        on_click=on_region_selected,
    )
    sg = ScrollingGroup(
        regions,
        id='regions',
        width=1,
        height=10,
    )
    return sg


async def get_region_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: Repo = dialog_manager.data['repo']
    regions = await repo.region_dao.get_regions()
    dialog_manager.current_context().dialog_data['parent_id'] = None
    return {
        "regions": regions,
    }


async def on_region_selected(c: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    await dialog_manager.dialog().next()
    dialog_manager.current_context().dialog_data['region_id'] = int(item_id)


CHOOSE_REGION_MESSAGE = "Выберите регион!"


class RegionWindow(Window):
    def __init__(self, state: State, prev: Type[Back | Cancel] = Back):
        regions = get_region_keyboard()
        super().__init__(
            Const(CHOOSE_REGION_MESSAGE),
            regions,
            prev(text=Const('Назад')),
            getter=get_region_data,
            state=state,
        )