from typing import Any

from aiogram.dispatcher.filters.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Column,
    Group,
    Next,
    Select,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from ecology_bot.presentors.bot.dialogs.messages import (
    DEFAULT_MESSAGES,
    ON_HELP_TEXT,
    ON_RETURN_TEXT,
    ON_START_TEXT,
)
from ecology_bot.presentors.bot.dialogs.states import (
    MainSG,
    OrganizationManagementSG,
    ProfileManagementSG,
    RegisterOrganizationSG,
    RegisterProfileSG,
)
from ecology_bot.presentors.bot.services.repo import Repo
from ecology_bot.presentors.bot.windows.global_event_window import GlobalEventWindow


def has_profile(data: dict, whenable: Any, manager: DialogManager):
    return data["dialog_data"].get("has_profile", False)


def has_on_startup_messages(data: dict, whenable: Any, manager: DialogManager):
    return bool(data["dialog_data"].get(ON_START_TEXT))


def has_unchecked_org(data: dict, whenable: Any, manager: DialogManager):
    return data["dialog_data"].get("has_unchecked_org", True)


def has_checked_org(data: dict, whenable: Any, manager: DialogManager):
    return data["dialog_data"].get("has_checked_org", False)


def has_active_global_event(data: dict, whenable: Any, manager: DialogManager):
    return data["dialog_data"].get("has_active_global_event", False)


async def get_org_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data["repo"]
    return {
        "orgs": await repo.organization_dao.get_organizations_by_creator(
            telegram_id=dialog_manager.event.from_user.id,
            is_checked=True,
        )
    }


async def get_help_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo = dialog_manager.data["repo"]
    return dict(
        help_text=await repo.text_chunk_dao.get_text(
            key=ON_HELP_TEXT,
            default=DEFAULT_MESSAGES[ON_HELP_TEXT],
        )
    )


async def process_result(start_data: Data, result: Any, manager: DialogManager):
    await on_start(None, manager)


async def on_start(self, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    repo: Repo = manager.data["repo"]
    user = await repo.user_dao.get_user(telegram_id=telegram_id)
    dialog_data = manager.current_context().dialog_data
    if user is not None:
        dialog_data["is_known_user"] = True
        if user.profile is not None:
            dialog_data["has_profile"] = True
        else:
            dialog_data["has_profile"] = False
        unchecked_orgs = await repo.organization_dao.get_organizations_by_creator(
            telegram_id=telegram_id, is_checked=False
        )
        dialog_data["has_unchecked_org"] = bool(unchecked_orgs)
        checked_orgs = await repo.organization_dao.get_organizations_by_creator(
            telegram_id=telegram_id, is_checked=True
        )
        dialog_data["has_checked_org"] = bool(checked_orgs)
    else:
        dialog_data["is_known_user"] = False
        await repo.user_dao.create_user(telegram_id=telegram_id, is_admin=False)
    d = await repo.global_event_dao.get_active_global_events()
    dialog_data["has_active_global_event"] = bool(d)


def get_help_window() -> Window:
    return Window(
        Format("{help_text}"),
        Back(Const("Назад")),
        state=MainSG.help,
        getter=get_help_data,
    )


async def on_org_selected(
    c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    await manager.start(
        state=OrganizationManagementSG.menu, data={"organization_id": int(item_id)}
    )


def get_org_keyboard() -> Group:
    orgs = Select(
        Format("{item.name}"),
        id="s_orgs",
        item_id_getter=lambda x: x.id,
        items="orgs",
        on_click=on_org_selected,
    )
    return Column(orgs)


def get_org_list_window() -> Window:
    orgs = get_org_keyboard()
    return Window(
        Const("Выберите организацию"),
        orgs,
        SwitchTo(
            id="switch_to_main_menu",
            state=MainSG.main,
            text=Const("Назад"),
        ),
        state=MainSG.org_list,
        getter=get_org_data,
    )


class MainMenuWindow(Window):
    def __init__(self):
        super().__init__(
            Format("{start_message}"),
            Start(
                text=Const("Зарегистрировать профиль волонтера"),
                id="register_volunteer_profile",
                state=RegisterProfileSG.region,
                when=lambda d, w, m: not has_profile(d, w, m),
            ),
            Start(
                text=Const("Перейти к профилю волонтера"),
                when=has_profile,
                id="go_volunteer_profile",
                state=ProfileManagementSG.main,
            ),
            Next(text=Const("Что может этот бот?")),
            Start(
                text=Const("Добавьте свою организацию"),
                id="register_organization",
                state=RegisterOrganizationSG.activity,
                when=lambda d, w, m: not has_unchecked_org(d, w, m),
            ),
            SwitchTo(
                text=Const("Перейти к меню организации"),
                id="switch_to_org_list",
                state=MainSG.org_list,
                when=has_checked_org,
            ),
            # SwitchTo(
            #     text=Const("Мероприятия"),
            #     id="switch_to_global_event_list",
            #     state=MainSG.global_event_list,
            #     when=has_active_global_event,
            # ),
            Select(
                Format("{item.name}"),
                id="s_globa_events",
                item_id_getter=lambda x: x.id,
                items="global_events",
                on_click=self.on_click(next_state=MainSG.global_event),
            ),
            state=MainSG.main,
            getter=self.get_data(),
        )

    def get_data(self):
        async def get_window_data(dialog_manager: DialogManager, **kwargs) -> dict:
            repo = dialog_manager.data["repo"]
            messages = []
            if dialog_manager.current_context().dialog_data["is_known_user"]:
                messages.append(
                    await repo.text_chunk_dao.get_text(
                        key=ON_RETURN_TEXT, default=DEFAULT_MESSAGES[ON_RETURN_TEXT]
                    )
                )
            else:
                messages.append(
                    await repo.text_chunk_dao.get_text(
                        key=ON_START_TEXT,
                        default=DEFAULT_MESSAGES[ON_START_TEXT],
                    )
                )
            return {
                "start_message": "\n".join(messages),
                "global_events": await repo.global_event_dao.get_active_global_events(),
            }

        return get_window_data

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


def get_dialog() -> Dialog:
    main_menu_window = MainMenuWindow()
    # global_event_list_window = GlobalEventListWindow(
    #     state=MainSG.global_event_list,
    #     next_state=MainSG.global_event,
    #     prev_state=MainSG.main,
    # )
    global_event_window = GlobalEventWindow(
        state=MainSG.global_event,
        prev_state=MainSG.main,
    )
    help_window = get_help_window()
    org_list_window = get_org_list_window()
    main_menu = Dialog(
        main_menu_window,
        help_window,
        org_list_window,
        # global_event_list_window,
        global_event_window,
        on_process_result=process_result,
        on_start=on_start,
    )
    return main_menu
