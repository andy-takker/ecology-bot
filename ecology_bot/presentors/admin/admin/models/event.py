from ecology_bot.admin.admin.view import SecureModelView


class EventModelView(SecureModelView):
    column_list = [
        "name",
        "description",
        "organization",
        "type",
    ]
    column_labels = {
        "organization": "Организация",
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "name": "Название",
        "description": "Описание",
        "type": "Тип",
        "district": "Район",
        "eco_activities": "Активности",
        "volunteer_types": "Виды волонтеров",
    }
    form_columns = [
        "name",
        "description",
        "organization",
        "district",
        "type",
        "volunteer_types",
    ]
