from flask_admin.contrib.sqla.fields import QuerySelectField
from wtforms import Form, StringField
from wtforms.validators import DataRequired

from ecology_bot.adapters.database.models import GlobalEvent
from ecology_bot.admin.admin.utils.text_area_field import CKTextAreaField
from ecology_bot.admin.admin.view import SecureModelView
from ecology_bot.database.engine import get_admin_db
from ecology_bot.workers.mailing import execute_global_mailing


class GlobalMailingForm(Form):
    name = StringField(
        label="Название",
        validators=[DataRequired(message="Обязательное поле!")],
        description="Название события",
    )
    global_event = QuerySelectField(
        label="Глобальное событие (мероприятие)",
        validators=[DataRequired(message="Обязательное поле!")],
        allow_blank=True,
        query_factory=lambda: get_admin_db()
        .session.query(GlobalEvent)
        .filter_by(is_active=True),
    )
    description = CKTextAreaField(
        label="Описание",
        description="Отображается в карточке мероприятия",
        validators=[DataRequired(message="Обязательное поле!")],
    )


class GlobalMailingModelView(SecureModelView):
    extra_js = ["https://cdn.ckeditor.com/4.6.0/standard/ckeditor.js"]
    can_edit = False

    column_list = [
        "created_at",
        "name",
        "global_event.name",
    ]
    column_default_sort = ("created_at", True)
    column_filters = ["name", "created_at"]
    column_searchable_list = ["name"]
    column_labels = {
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "name": "Название",
        "description": "Описание",
        "global_event.name": "Глобальное мероприятие",
    }
    form = GlobalMailingForm

    def create_model(self, form):
        model = super().create_model(form)
        if model:
            execute_global_mailing.delay(model.id)
        return model
