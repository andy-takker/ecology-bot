from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

from ecology_bot.adapters.database.models import (
    Activity,
    AwesomeData,
    District,
    Event,
    GlobalEvent,
    GlobalEventUser,
    GlobalMailing,
    Organization,
    Profile,
    Region,
    TextChunk,
    User,
    VolunteerType,
)
from ecology_bot.admin.admin.models import (
    ActivityModelView,
    AwesomeDataModelView,
    DistrictModelView,
    EventModelView,
    GlobalEventModelView,
    GlobalEventUserModelView,
    GlobalMailingModelView,
    OrganizationModelView,
    ProfileModelView,
    RegionModelView,
    TextChunkModelView,
    UserModelView,
    VolunteerTypeModelView,
)
from ecology_bot.admin.admin.pages.auth import LoginLink, LoginView, LogoutLink
from ecology_bot.admin.admin.pages.home import HomeAdminIndexView


def register_admin(flask_app: Flask, database: SQLAlchemy):
    """Регистрирует расширение админ-панели"""
    admin = Admin(
        app=flask_app,
        name="Эковолонтерские организации",
        template_mode="bootstrap4",
        index_view=HomeAdminIndexView(name="Главная", url="/"),
        endpoint="admin",
        url="/",
    )
    model_views = {
        Activity: ActivityModelView,
        AwesomeData: AwesomeDataModelView,
        District: DistrictModelView,
        Event: EventModelView,
        GlobalEvent: GlobalEventModelView,
        GlobalEventUser: GlobalEventUserModelView,
        GlobalMailing: GlobalMailingModelView,
        Organization: OrganizationModelView,
        Profile: ProfileModelView,
        Region: RegionModelView,
        TextChunk: TextChunkModelView,
        User: UserModelView,
        VolunteerType: VolunteerTypeModelView,
    }
    for model, model_view in model_views.items():
        admin.add_view(
            model_view(
                model=model,
                session=database.session,
                name=model.__verbose_name_plural__,
                endpoint=model.__admin_endpoint__,
                category="Данные",
            )
        )
    # admin.add_view(
    #     RegionModelView(
    #         model=Region,
    #         session=database.session,
    #         name="Регионы",
    #         endpoint="regions",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     ProfileModelView(
    #         model=Profile,
    #         session=database.session,
    #         name="Профили волонтеров",
    #         endpoint="profiles",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     DistrictModelView(
    #         model=District,
    #         session=database.session,
    #         name="Районы",
    #         endpoint="districts",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     VolunteerTypeModelView(
    #         model=VolunteerType,
    #         session=database.session,
    #         name="Виды волонтерств",
    #         endpoint="volunteer_types",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     ActivityModelView(
    #         model=Activity,
    #         session=database.session,
    #         name="Активности",
    #         endpoint="eco_activities",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     OrganizationModelView(
    #         model=Organization,
    #         session=database.session,
    #         name="Организации",
    #         endpoint="organizations",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     EventModelView(
    #         model=Event,
    #         session=database.session,
    #         name="События",
    #         endpoint="events",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     GlobalEventModelView(
    #         model=GlobalEvent,
    #         session=database.session,
    #         name=GlobalEvent.__verbose_name_plural__,
    #         endpoint=GlobalEvent.__admin_endpoint__,
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     UserModelView(
    #         model=User,
    #         session=database.session,
    #         name="Пользователи",
    #         endpoint="users",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     TextChunkModelView(
    #         model=TextChunk,
    #         session=database.session,
    #         name="Тексты бота",
    #         endpoint="text_chunks",
    #         category="Данные",
    #     )
    # )
    # admin.add_view(
    #     AwesomeDataModelView(
    #         model=AwesomeData,
    #         session=database.session,
    #         name="Данные от пользователей",
    #         endpoint="awesome_data",
    #         category="Данные",
    #     )
    # )
    admin.add_link(LoginLink(name="Login"))
    admin.add_link(LogoutLink(name="Logout", url="logout/"))
    admin.add_view(LoginView(name="Login", url="login/", endpoint="login"))
