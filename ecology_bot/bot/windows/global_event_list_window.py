from typing import Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format, Const

from ecology_bot.bot.dialogs.messages import DEFAULT_MESSAGES, ON_GLOBAL_EVENT_LIST


class GlobalEventListWindow(Window):
    def __init__(self, state: State, next_state: State, prev_state: State):
        global_events = self.get_global_event_keyboard(next_state=next_state)
        super().__init__(
            Format("{global_event_list_message}"),
            global_events,
            SwitchTo(
                text=Const("Назад"),
                id="switch_to_start_menu",
                state=prev_state,
            ),
            state=state,
            getter=self.get_data(),
        )

    def get_data(self):
        async def get_window_data(dialog_manager: DialogManager, **kwargs) -> dict:
            repo = dialog_manager.data["repo"]
            return {
                "global_event_list_message": await repo.text_chunk_dao.get_text(
                    key=ON_GLOBAL_EVENT_LIST,
                    default=DEFAULT_MESSAGES[ON_GLOBAL_EVENT_LIST],
                ),
                "global_events": await repo.global_event_dao.get_active_global_events(),
            }

        return get_window_data

    def get_global_event_keyboard(
        self, next_state: State | None = None
    ) -> ScrollingGroup:
        global_events = Select(
            Format("{item.name}"),
            id="s_global_events",
            item_id_getter=lambda x: x.id,
            items="global_events",
            on_click=self.on_click(next_state),
        )
        sg = ScrollingGroup(
            global_events,
            id="global_events",
            width=1,
            height=10,
        )
        return sg

    def on_click(self, next_state: State | None = None):
        async def on_global_event_selected(
            c: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
        ):
            if next_state is not None:
                await dialog_manager.dialog().switch_to(next_state)
            else:
                await dialog_manager.dialog().next()
            dialog_manager.current_context().dialog_data["global_event_id"] = int(
                item_id
            )

        return on_global_event_selected
