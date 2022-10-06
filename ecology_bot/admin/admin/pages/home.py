from dataclasses import dataclass

from flask import url_for
from flask_admin import AdminIndexView, expose

from ecology_bot.database.engine import get_admin_db
from ecology_bot.database.models import (
    Activity,
    AwesomeData,
    District,
    Employee,
    Event,
    Mailing,
    Organization,
    Profile,
    Region,
    TextChunk,
    User,
    VolunteerType,
)


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
            Organization,
            Profile,
            Region,
            TextChunk,
            User,
            VolunteerType,
        )
        models_data = []
        for model in models:
            models_data.append(
                ModelData(
                    verbose_name=model.__verbose_name_plural__,
                    total_objs=db.session.query(model).count(),
                    url=url_for(model.__admin_endpoint__ + ".index_view"),
                )
            )
        print(Activity.__verbose_name_plural__)
        return self.render(
            template="admin_panel/home.html",
            models_data=models_data,
        )
