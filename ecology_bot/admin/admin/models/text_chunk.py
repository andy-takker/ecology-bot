from string import ascii_lowercase, digits

from flask import flash, current_app
from flask_admin.babel import gettext
from wtforms import (
    Field,
    ValidationError,
    Form,
    SelectField,
    IntegerField,
)
from wtforms.validators import DataRequired, NumberRange

from ecology_bot.admin.admin.utils.text_area_field import CKTextAreaField
from ecology_bot.admin.admin.view import SecureModelView
from ecology_bot.bot.dialogs.messages import MESSAGE_KEYS
from ecology_bot.database.models import TextChunk

SYMBOLS = ascii_lowercase + digits + "_"

KEY_NAME_ERROR = (
    "Ключ должен состоять только из латинских букв, цифр, знака подчеркивания "
)


def validate_key(form, field: Field):
    for letter in field.data:
        if letter not in SYMBOLS:
            raise ValidationError(KEY_NAME_ERROR)


from ecology_bot.utils.get_settings import get_settings


class TextChunkForm(Form):
    key = SelectField(
        label="Сообщение",
        validators=[DataRequired(message="Обязательное поле!"), validate_key],
        choices=MESSAGE_KEYS,
    )
    weight = IntegerField(
        label="Вес",
        default=0,
        description="Чем больше вес, тем выше будет текст",
        validators=[
            NumberRange(min=0, max=1000),
            DataRequired(message="Обязательное поле!"),
        ],
    )
    text = CKTextAreaField(
        label="Текст",
        description="Само сообщение",
        validators=[DataRequired(message="Обязательное поле!")],
    )


class TextChunkModelView(SecureModelView):
    extra_js = ["https://cdn.ckeditor.com/4.6.0/standard/ckeditor.js"]

    column_list = ["created_at", "key", "weight", "description"]
    column_default_sort = [("key", True), ("weight", True)]
    column_labels = {
        "created_at": "Дата создания",
        "key": "Идентификатор",
        "description": "Описание",
        "text": "Текст",
        "weight": "Вес",
    }
    form = TextChunkForm

    def create_model(self, form):
        weight = form.weight.data
        key = form.key.data
        text = (
            self.session.query(TextChunk)
            .filter(
                TextChunk.weight == weight,
                TextChunk.key == key,
            )
            .first()
        )
        if text is not None:
            flash(
                gettext(
                    "Failed to create record. %(error)s",
                    error="Запись с таким ключом и весом уже была создана!",
                ),
                "error",
            )
            self.session.rollback()
            return False
        current_app.extensions["redis"].delete("text_chunk:" + key)
        return super().create_model(form)

    def delete_model(self, model: TextChunk):
        super().delete_model(model)
        current_app.extensions["redis"].delete("text_chunk:" + model.key)
