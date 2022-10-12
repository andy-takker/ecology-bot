from ecology_bot.admin.admin.view import SecureModelView


class GlobalEventModelView(SecureModelView):
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
    form_columns = ["name", "is_active"]
