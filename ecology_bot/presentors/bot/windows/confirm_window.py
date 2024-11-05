from collections.abc import Callable

from aiogram.dispatcher.filters.state import State
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Row
from aiogram_dialog.widgets.text import Const, Format


class ConfirmWindow(Window):
    def __init__(self, state: State, text: str, on_confirm: Callable, getter=None):
        super().__init__(
            Format(text=text),
            Row(
                Back(Const("Нет")),
                Button(Const("Да"), id="confirm", on_click=on_confirm),
            ),
            state=state,
            getter=getter,
        )
