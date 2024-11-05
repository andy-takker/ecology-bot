from collections import namedtuple
from typing import Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Column, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.adapters.database.models import EventType

EventTypeData = namedtuple("EventTypeData", ["name", "type", "id"])

EVENT_TYPES: dict[int, EventTypeData] = {
    1: EventTypeData(name="Объявление о мероприятии", type=EventType.DEFAULT, id="1"),
    2: EventTypeData(
        name="Нужны волонтеры на мероприятие", type=EventType.RECRUITMENT, id="2"
    ),
}


async def get_event_types(dialog_manager: DialogManager, **kwargs):
    return {"event_types": EVENT_TYPES.values()}


class EventTypeWindow(Window):
    def __init__(self, state: State, event_type_states: dict[EventType, State]):
        async def on_event_type_selected(
            c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
        ):
            event_type = EVENT_TYPES[int(item_id)].type
            manager.current_context().dialog_data["event_type"] = event_type.value
            await manager.dialog().switch_to(state=event_type_states[event_type])

        event_type_keyboard = self.get_event_type_keyboard(on_event_type_selected)
        super().__init__(
            Const("Выберите тип объявления:"),
            event_type_keyboard,
            Back(text=Const("Назад")),
            state=state,
            getter=get_event_types,
        )

    @staticmethod
    def get_event_type_keyboard(on_event_type_selected) -> Group:
        event_types = Select(
            Format("{item.name}"),
            id="s_event_types",
            item_id_getter=lambda x: x.id,
            items="event_types",
            on_click=on_event_type_selected,
        )
        return Column(event_types)
