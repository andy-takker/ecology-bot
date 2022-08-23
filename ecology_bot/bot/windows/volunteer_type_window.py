from typing import Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Multiselect, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.bot.services.repo import Repo
from ecology_bot.bot.utils.switch_to_button import GoTo


async def save_volunteer_type(c: CallbackQuery, widget: Any, manager: DialogManager):
    widget = manager.dialog().find('m_volunteer_types')
    volunteer_type_ids = list(map(int, widget.get_checked()))
    manager.current_context().dialog_data['volunteer_type'] = volunteer_type_ids


async def get_volunteer_type_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data['repo']
    return {
        'volunteer_types': await repo.volunteer_type_dao.get_volunteer_types()
    }


class VolunteerTypeWindow(Window):
    def __init__(self, state: State, prev_state: State, next_state: State):
        volunteer_types = self.get_keyboard()
        getter = get_volunteer_type_data
        super().__init__(
            Const('Выберите какие типы волонтеров требуются:'),
            volunteer_types,
            SwitchTo(text=Const('Далее'), id='switch_to_next', state=next_state, on_click=save_volunteer_type),
            GoTo(text='Назад', id='switch_to_back', state=prev_state),
            getter=getter,
            state=state,
        )

    def get_keyboard(self) -> ScrollingGroup:
        el_id = 'm_volunteer_types'
        getter = lambda x: x.id
        items = 'volunteer_types'
        volunteer_types = Multiselect(
            Format("\U00002705 {item.name}"),
            Format("{item.name}"),
            id=el_id,
            item_id_getter=getter,
            items=items,
        )
        sg = ScrollingGroup(
            volunteer_types,
            id='volunteer_types',
            width=1,
            height=10,
        )
        return sg
