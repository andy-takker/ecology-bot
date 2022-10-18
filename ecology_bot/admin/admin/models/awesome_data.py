from ecology_bot.admin.admin.view import SecureModelView


class AwesomeDataModelView(SecureModelView):
    can_edit = False
    can_delete = True
    column_list = [
        "from_user_id",
        "description",
        "data",
    ]
    column_searchable_list = [
        "description",
        "data",
    ]
    column_labels = {
        "from_user_id": "От пользователя",
        "description": "Описание",
        "data": "Данные",
    }
    column_sortable_list = ["description", "from_user_id"]


IOError