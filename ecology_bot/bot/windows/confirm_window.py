from aiogram.dispatcher.filters.state import State
from aiogram_dialog import Window
from typing import Callable

from aiogram_dialog.widgets.kbd import Row, Back, Button
from aiogram_dialog.widgets.text import Format, Const


class ConfirmWindow(Window):
    def __init__(self, state: State, text: str, on_confirm: Callable, getter=None):
        super().__init__(
            Format(text=text),
            Row(Back(Const("Нет")), Button(Const("Да"), id='confirm', on_click=on_confirm)),
            state=state,
            getter=getter,
        )
