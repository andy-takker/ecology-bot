from collections.abc import Callable

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Text


class StartBtn(Start):
    def __init__(
        self, id: str, state: State, text: Text, getter: Callable = None, on_click=None
    ):
        super().__init__(id="create_event", state=state, text=text, on_click=on_click)
        self.getter = getter

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        if self.user_on_click:
            await self.user_on_click(c, self, manager)
        if self.getter:
            self.start_data = await self.getter(c, self, manager)
        await manager.start(self.state, self.start_data, self.mode)
