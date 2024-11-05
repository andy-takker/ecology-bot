from collections.abc import Awaitable, Callable, Coroutine

from aiogram.dispatcher.filters.state import State
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd.button import OnClick
from aiogram_dialog.widgets.text import Format

from ecology_bot.presentors.bot.utils.switch_to_button import GoTo


def default_handler(id) -> Awaitable:
    async def input_handler(m: Message, dialog: Dialog, manager: DialogManager):
        manager.current_context().dialog_data[id] = m.text
        await dialog.next(manager)

    return input_handler


class InputTextWindow(Window):
    def __init__(
        self,
        id: str,
        getter_text: Callable,
        state: State,
        get_prev_state: OnClick | None,
        handler: Coroutine = None,
    ):
        if handler is None:
            handler = default_handler(id)
        super().__init__(
            Format("{text}"),
            GoTo(
                text="Назад",
                id="switch_to_btn",
                state=get_prev_state,
            ),
            MessageInput(handler),
            getter=getter_text,
            state=state,
        )
