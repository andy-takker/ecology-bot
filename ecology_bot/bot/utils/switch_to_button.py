from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.kbd.button import OnClick
from aiogram_dialog.widgets.kbd.state import EventProcessorButton
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.when import WhenCondition


class GoTo(EventProcessorButton):
    def __init__(
        self,
        text: str,
        id: str,
        state: OnClick | State,
        when: WhenCondition = None,
    ):
        self.state = state
        super().__init__(
            id=id,
            text=Const(text),
            on_click=self._on_click,
            when=when,
        )

    async def _on_click(self, c: CallbackQuery, button: Button, manager: DialogManager):
        state = self.state
        if not isinstance(self.state, State):
            state = await self.state(c, self, manager)
        await manager.dialog().switch_to(state)
