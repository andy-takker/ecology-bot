from typing import Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.presentors.bot.dialogs.messages import (
    DEFAULT_MESSAGES,
    ON_SUBSCRIBE_GLOBAL_EVENT,
    ON_UNSUBSCRIBE_GLOBAL_EVENT,
)
from ecology_bot.presentors.bot.services.repo import Repo
from ecology_bot.presentors.bot.utils.switch_to_button import GoTo


def get_data():
    async def get_window_data(dialog_manager: DialogManager, **kwargs) -> dict:
        repo: Repo = dialog_manager.data["repo"]
        telegram_id = dialog_manager.event.from_user.id
        user = await repo.user_dao.get_user(telegram_id=telegram_id)
        global_event_id = dialog_manager.current_context().dialog_data[
            "global_event_id"
        ]
        global_event = await repo.global_event_dao.get_global_event(
            global_event_id=global_event_id
        )
        global_event_user = await repo.global_event_dao.get_global_event_user(
            user_id=user.id,
            global_event_id=global_event_id,
        )
        return {
            "user": user,
            "global_event": global_event,
            "global_event_user": global_event_user,
        }

    return get_window_data


def is_subscribed(data: dict, whenable: Any, manager: DialogManager):
    return bool(data.get("global_event_user"))


class GlobalEventWindow(Window):
    def __init__(self, state: State, prev_state: State):
        super().__init__(
            Format("{global_event.name}\n"),
            Format("{global_event.clean_description}"),
            Button(
                text=Const("Подписаться"),
                id="subscribe",
                when=lambda d, w, m: not is_subscribed(d, w, m),
                on_click=self.click_on_subscribe(state),
            ),
            Button(
                text=Const("Отписаться"),
                id="unsubscribe",
                when=is_subscribed,
                on_click=self.click_on_unsubscribe(state=state),
            ),
            GoTo("Назад", id="back_to_list", state=prev_state),
            state=state,
            getter=get_data(),
        )

    def click_on_subscribe(self, state: State):
        async def on_click(c: CallbackQuery, button: Button, manager: DialogManager):
            repo: Repo = manager.data["repo"]
            telegram_id = manager.event.from_user.id
            user = await repo.user_dao.get_user(telegram_id=telegram_id)
            global_event = await repo.global_event_dao.get_global_event(
                manager.current_context().dialog_data["global_event_id"]
            )

            await repo.global_event_dao.create_global_event_user(
                user_id=user.id,
                global_event_id=global_event.id,
            )
            await manager.dialog().switch_to(state=state)
            message = await repo.text_chunk_dao.get_text(
                key=ON_SUBSCRIBE_GLOBAL_EVENT,
                default=DEFAULT_MESSAGES[ON_SUBSCRIBE_GLOBAL_EVENT],
            )
            await c.bot.answer_callback_query(c.id, message, show_alert=True)

        return on_click

    def click_on_unsubscribe(self, state: State):
        async def on_click(c: CallbackQuery, button: Button, manager: DialogManager):
            repo: Repo = manager.data["repo"]
            telegram_id = manager.event.from_user.id
            user = await repo.user_dao.get_user(telegram_id=telegram_id)
            global_event = await repo.global_event_dao.get_global_event(
                manager.current_context().dialog_data["global_event_id"]
            )

            await repo.global_event_dao.delete_global_event(
                user_id=user.id,
                global_event_id=global_event.id,
            )
            await manager.dialog().switch_to(state=state)
            message = await repo.text_chunk_dao.get_text(
                key=ON_UNSUBSCRIBE_GLOBAL_EVENT,
                default=DEFAULT_MESSAGES[ON_UNSUBSCRIBE_GLOBAL_EVENT],
            )
            await c.bot.answer_callback_query(c.id, message, show_alert=True)

        return on_click
