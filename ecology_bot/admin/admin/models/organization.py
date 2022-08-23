from ecology_bot.admin.admin.models.view import SecureModelView


class OrganizationModelView(SecureModelView):
    column_list = ["name", "is_checked", "creator", "district", "activities"]
    column_searchable_list = ["name"]
    column_labels = {
        "creator": "Создатель организации",
        "activities": "Активности",
        "district": "Район",
        "events": "События",
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "name": "Название",
        "is_checked": "Проверена?",
        "is_superorganization": "Суперорганизация?",
    }
    column_sortable_list = ['name']