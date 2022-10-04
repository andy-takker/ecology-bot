from wtforms import Field, ValidationError

from ecology_bot.admin.admin.models.view import SecureModelView

from string import ascii_lowercase, digits

SYMBOLS = ascii_lowercase + digits + '_'

KEY_NAME_ERROR = (
    'Ключ должен состоять только из латинских букв, цифр, знака подчеркивания '
)


def validate_key(form, field: Field):
    for letter in field.data:
        if letter not in SYMBOLS:
            raise ValidationError(KEY_NAME_ERROR)


class TextChunkModelView(SecureModelView):
    column_list = ['created_at', 'key', 'weight', 'description']
    column_default_sort = [('key', True), ('weight', True)]

    form_args = {
        'key': {
            'validators': [validate_key],
        }
    }
    column_labels = {
        'created_at': 'Дата создания',
        'key': 'Идентификатор',
        'description': 'Описание',
        'text': 'Текст',
        'weight': 'Вес',
    }
