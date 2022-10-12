from typing import Type, Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Back, Cancel, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.bot.services.repo import Repo
from ecology_bot.bot.utils.switch_to_button import GoTo


async def get_region_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo: Repo = dialog_manager.data["repo"]
    regions = await repo.region_dao.get_regions()
    dialog_manager.current_context().dialog_data["parent_id"] = None
    return {
        "regions": regions,
    }


CHOOSE_REGION_MESSAGE = "Выберите регион!"


class RegionWindow(Window):
    def __init__(
        self,
        state: State,
        not_region_state: State,
        next_state: State,
        prev: Type[Back | Cancel] = Back,
    ):
        regions = self.get_region_keyboard(next_state=next_state)
        super().__init__(
            Const(CHOOSE_REGION_MESSAGE),
            regions,
            GoTo(
                text="Моего региона нет в списке",
                id="goto_not_regions",
                state=not_region_state,
            ),
            prev(text=Const("Назад")),
            getter=get_region_data,
            state=state,
        )

    def get_region_keyboard(self, next_state: State | None = None) -> ScrollingGroup:
        regions = Select(
            Format("{item.name}"),
            id="s_regions",
            item_id_getter=lambda x: x.id,
            items="regions",
            on_click=self.on_click(next_state),
        )
        sg = ScrollingGroup(
            regions,
            id="regions",
            width=1,
            height=10,
        )
        return sg

    def on_click(self, next_state: State | None = None):
        async def on_region_selected(
            c: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
        ):
            if next_state is not None:
                await dialog_manager.dialog().switch_to(next_state)
            else:
                await dialog_manager.dialog().next()
            dialog_manager.current_context().dialog_data["region_id"] = int(item_id)

        return on_region_selected
