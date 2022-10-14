from wtforms import Form, StringField, BooleanField
from wtforms.validators import DataRequired

from ecology_bot.admin.admin.utils.text_area_field import CKTextAreaField
from ecology_bot.admin.admin.view import SecureModelView


class GlobalEventForm(Form):
    name = StringField(
        label="Название",
        validators=[DataRequired(message="Обязательное поле!")],
        description="Название события",
    )
    is_active = BooleanField(
        label="Активный проект?",
        description="Бот показывает только активные мероприятия",
    )
    description = CKTextAreaField(
        label="Описание",
        description="Отображается в карточке мероприятия",
        validators=[DataRequired(message="Обязательное поле!")],
    )


class GlobalEventModelView(SecureModelView):
    extra_js = ["https://cdn.ckeditor.com/4.6.0/standard/ckeditor.js"]

    column_list = [
        "created_at",
        "name",
        "is_active",
    ]
    column_default_sort = ("name", False)
    column_filters = ["name", "is_active"]
    column_searchable_list = ["name"]
    column_labels = {
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "name": "Название",
        "is_active": "Активен?",
    }
    column_descriptions = {
        "is_active": "Активные события отображаются у пользователей в ленте"
    }
    form = GlobalEventForm
