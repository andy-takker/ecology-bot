from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, Data
from aiogram_dialog.widgets.kbd import Button, Back, SwitchTo, Select, Column, Group, Start, Next
from aiogram_dialog.widgets.text import Const, Format
from loguru import logger

from ecology_bot.bot.dialogs.states import MainSG, RegisterProfileSG, RegisterOrganizationSG, ProfileManagementSG, \
    OrganizationManagementSG
from ecology_bot.bot.services.repo import Repo

ONBOARDING_MESSAGE = (
    "Привет!\n"
    "Это пилотная версия экобота Союза эковолонтерских "
    "организаций.\nЗдесь Вы сможете узнать об экологических "
    "мероприятиях и проектах, стать волонтёром или найти "
    "единомышленников.\n Сейчас бот работает с Ленинградской"
    " областью, но далее охватит другие регионы.\n"
    "Помогите улучшить бота: опробуйте весь функционал."
)

RETURN_MESSAGE = "С возвращением!"

HELP_MESSAGE = "С помощью бота волонтеры могут получать персонализированные " \
               "уведомления о мероприятиях и волонтерских вакансиях в своем " \
               "районе, а экологически активные сообщества - найти волонтеров и" \
               " привлечь участников на свои мероприятия и акции.\n\nБот может " \
               "пригласить Вас в чат, где собрались экоактивисты из вашего " \
               "района. Общайтесь, делитесь опытом, объединяйтесь для создания" \
               " экособытий!\n\nСовсем скоро всем пользователям бота будет " \
               "доступна справочная информация: адреса пунктов приема " \
               "вторсырья, контакты движений и организаций.\n\n" \
               "Пока работает пилотная версия, функционал будет расширяться."


def is_known_user(data: dict, whenable: Any, manager: DialogManager):
    return data['dialog_data'].get('is_known_user', False)


def has_profile(data: dict, whenable: Any, manager: DialogManager):
    return data['dialog_data'].get('has_profile', False)


def has_on_startup_messages(data: dict, whenable: Any, manager: DialogManager):
    return bool(data['dialog_data'].get('texts'))


def has_unchecked_org(data: dict, whenable: Any, manager: DialogManager):
    return data['dialog_data'].get('has_unchecked_org', True)


def has_checked_org(data: dict, whenable: Any, manager: DialogManager):
    return data['dialog_data'].get('has_checked_org', False)


async def get_org_data(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.data['repo']
    return {
        "orgs": await repo.organization_dao.get_organizations_by_creator(
            telegram_id=dialog_manager.event.from_user.id,
            is_checked=True,
        )
    }


async def get_help_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo = dialog_manager.data['repo']
    help_text = '\n'.join(await repo.text_chunk_dao.get_by_key(key='help_text'))
    return dict(help_text=help_text)


async def get_window_data(dialog_manager: DialogManager, **kwargs) -> dict:
    repo = dialog_manager.data['repo']
    texts = '\n'.join(await repo.text_chunk_dao.get_by_key(key='start_text'))
    dialog_manager.data['texts'] = True
    return {
        "texts": texts,
    }


async def process_result(start_data: Data, result: Any, manager: DialogManager):
    await on_start(None, manager)


async def on_start(self, manager: DialogManager):
    telegram_id = manager.event.from_user.id
    repo: Repo = manager.data['repo']
    user = await repo.user_dao.get_user(telegram_id=telegram_id)
    dialog_data = manager.current_context().dialog_data
    if user is not None:
        dialog_data['is_known_user'] = True
    else:
        dialog_data['is_known_user'] = False
        await repo.user_dao.create_user(telegram_id=telegram_id, is_admin=False)
        return
    if user.profile is not None:
        dialog_data['has_profile'] = True
    else:
        dialog_data['has_profile'] = False
    unchecked_orgs = await repo.organization_dao.get_organizations_by_creator(telegram_id=telegram_id, is_checked=False)
    dialog_data['has_unchecked_org'] = bool(unchecked_orgs)
    checked_orgs = await repo.organization_dao.get_organizations_by_creator(telegram_id=telegram_id, is_checked=True)
    dialog_data['has_checked_org'] = bool(checked_orgs)
    dialog_data['texts'] = '\n'.join(await repo.text_chunk_dao.get_by_key(key='on_startup_messages'))


def get_help_window() -> Window:
    return Window(
        Format("{help_text}"),
        Back(Const('Назад')),
        state=MainSG.help,
        getter=get_help_data,
    )


async def on_org_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    await manager.start(state=OrganizationManagementSG.menu, data={'organization_id': int(item_id)})


def get_org_keyboard() -> Group:
    orgs = Select(
        Format("{item.name}"),
        id='s_orgs',
        item_id_getter=lambda x: x.id,
        items='orgs',
        on_click=on_org_selected,
    )
    return Column(orgs)


def get_org_list_window() -> Window:
    orgs = get_org_keyboard()
    return Window(
        Const('Выберите организацию'),
        orgs,
        SwitchTo(
            id='switch_to_main_menu',
            state=MainSG.main,
            text=Const('Назад'),
        ),
        state=MainSG.org_list,
        getter=get_org_data,
    )


def get_main_menu_window() -> Window:
    return Window(
        Const('С возвращением', when=is_known_user),
        Const(ONBOARDING_MESSAGE, when=lambda d, w, m: not is_known_user(d, w, m)),
        Format('\n{texts}', when=lambda d, w, n: has_on_startup_messages(d, w, n)),
        Start(
            text=Const('Зарегистрировать профиль волонтера'),
            id='register_volunteer_profile',
            state=RegisterProfileSG.region,
            when=lambda d, w, m: not has_profile(d, w, m),
        ),
        Start(
            text=Const('Перейти к профилю волонтера'),
            when=has_profile,
            id='go_volunteer_profile',
            state=ProfileManagementSG.main,
        ),
        Next(text=Const('Что может этот бот?')),
        Start(
            text=Const('Добавьте свою организацию'),
            id='register_organization',
            state=RegisterOrganizationSG.activity,
            when=lambda d, w, m: not has_unchecked_org(d, w, m),
        ),
        SwitchTo(
            text=Const('Перейти к меню организации'),
            id='switch_to_org_list',
            state=MainSG.org_list,
            when=has_checked_org,
        ),
        state=MainSG.main,
        getter=get_window_data,
    )


def get_dialog() -> Dialog:
    main_menu_window = get_main_menu_window()
    help_window = get_help_window()
    org_list_window = get_org_list_window()
    main_menu = Dialog(
        main_menu_window,
        help_window,
        org_list_window,
        on_process_result=process_result,
        on_start=on_start,
    )
    return main_menu
