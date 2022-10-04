from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

from ecology_bot.admin.admin.models.awesome_data import AwesomeDataModelView
from ecology_bot.admin.admin.models.district import DistrictModelView
from ecology_bot.admin.admin.models.eco_activity import EcoActivityModelView
from ecology_bot.admin.admin.models.event import EventModelView
from ecology_bot.admin.admin.models.organization import OrganizationModelView
from ecology_bot.admin.admin.models.region import RegionModelView
from ecology_bot.admin.admin.models.text_chunk import TextChunkModelView
from ecology_bot.admin.admin.models.volunteer_type import VolunteerTypeModelView
from ecology_bot.admin.admin.models.user import UserModelView
from ecology_bot.admin.admin.pages.auth import LoginLink, LogoutLink, LoginView
from ecology_bot.admin.admin.pages.home import HomeAdminIndexView
from ecology_bot.database.models import (
    District,
    VolunteerType,
    Activity,
    Organization,
    Event, Region,
    User, TextChunk, AwesomeData,
)


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
    admin.add_view(
        RegionModelView(
            model=Region,
            session=database.session,
            name="Регионы",
            endpoint="regions",
            category='Данные',
        )
    )
    admin.add_view(
        DistrictModelView(
            model=District,
            session=database.session,
            name="Районы",
            endpoint="districts",
            category='Данные',
        )
    )
    admin.add_view(
        VolunteerTypeModelView(
            model=VolunteerType,
            session=database.session,
            name="Виды волонтерств",
            endpoint="volunteer_types",
            category='Данные', 
        )
    )
    admin.add_view(
        EcoActivityModelView(
            model=Activity,
            session=database.session,
            name="Активности",
            endpoint="eco_activities",
            category='Данные',
        )
    )
    admin.add_view(
        OrganizationModelView(
            model=Organization,
            session=database.session,
            name="Организации",
            endpoint="organizations",
            category='Данные',
        )
    )
    admin.add_view(
        EventModelView(
            model=Event,
            session=database.session,
            name="События",
            endpoint="events",
            category='Данные',
        )
    )
    admin.add_view(
        UserModelView(
            model=User,
            session=database.session,
            name='Пользователи',
            endpoint='users',
            category='Данные',
        )
    )
    admin.add_view(
        TextChunkModelView(
            model=TextChunk,
            session=database.session,
            name='Тексты бота',
            endpoint='text_chunks',
            category='Данные',
        )
    )
    admin.add_view(
        AwesomeDataModelView(
            model=AwesomeData,
            session=database.session,
            name='Данные от пользователей',
            endpoint='awesome_data',
            category='Данные',
        )
    )
    admin.add_link(LoginLink(name="Login"))
    admin.add_link(LogoutLink(name="Logout", url="logout/"))
    admin.add_view(LoginView(name="Login", url="login/", endpoint="login"))
