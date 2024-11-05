from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const

from ecology_bot.presentors.bot.dialogs.states import ProfileDeleteSG


async def on_delete(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done({"action": "delete_profile"})


def get_confirm_window():
    return Window(
        Const("Вы действительно хотите удалить профиль?"),
        Row(
            Cancel(Const("Нет")), Button(Const("Да"), id="confirm", on_click=on_delete)
        ),
        state=ProfileDeleteSG.confirm,
    )


def get_dialog() -> Dialog:
    confirm_window = get_confirm_window()
    return Dialog(
        confirm_window,
    )
