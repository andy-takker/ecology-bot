from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy

from ecology_bot.admin.admin.models.district import DistrictModelView
from ecology_bot.admin.admin.models.eco_activity import EcoActivityModelView
from ecology_bot.admin.admin.models.event import EventModelView
from ecology_bot.admin.admin.models.organization import OrganizationModelView
from ecology_bot.admin.admin.models.region import RegionModelView
from ecology_bot.admin.admin.models.volunteer_type import VolunteerTypeModelView
from ecology_bot.admin.admin.pages.auth import LoginLink, LogoutLink, LoginView
from ecology_bot.admin.admin.pages.home import HomeAdminIndexView
from ecology_bot.database.models import (
    District,
    VolunteerType,
    Activity,
    Organization,
    Event, Region,
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
        )
    )
    admin.add_view(
        DistrictModelView(
            model=District,
            session=database.session,
            name="Районы",
            endpoint="districts",
        )
    )
    admin.add_view(
        VolunteerTypeModelView(
            model=VolunteerType,
            session=database.session,
            name="Виды волонтерств",
            endpoint="volunteer_types",
        )
    )
    admin.add_view(
        EcoActivityModelView(
            model=Activity,
            session=database.session,
            name="Активности",
            endpoint="eco_activities",
        )
    )
    admin.add_view(
        OrganizationModelView(
            model=Organization,
            session=database.session,
            name="Организации",
            endpoint="organizations",
        )
    )
    admin.add_view(
        EventModelView(
            model=Event,
            session=database.session,
            name="События",
            endpoint="events",
        )
    )
    admin.add_link(LoginLink(name="Login"))
    admin.add_link(LogoutLink(name="Logout", url="logout/"))
    admin.add_view(LoginView(name="Login", url="login/", endpoint="login"))
