from dataclasses import dataclass

from flask import url_for
from flask_admin import AdminIndexView, expose

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
from ecology_bot.database.engine import get_admin_db


@dataclass
class ModelData:
    verbose_name: str
    total_objs: int
    url: str


class HomeAdminIndexView(AdminIndexView):
    """Главная страница"""

    @expose("/")
    def index(self):
        db = get_admin_db()
        models = (
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
        models_data = []
        for i, model in enumerate(models):
            if i % 3 == 0:
                models_data.append([])
            models_data[-1].append(
                ModelData(
                    verbose_name=model.__verbose_name_plural__,
                    total_objs=db.session.query(model).count(),
                    url=url_for(model.__admin_endpoint__ + ".index_view"),
                )
            )
        return self.render(
            template="admin_panel/home.html",
            models_data=models_data,
        )
