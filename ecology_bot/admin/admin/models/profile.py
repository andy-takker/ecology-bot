from ecology_bot.admin.admin.view import SecureModelView


class ProfileModelView(SecureModelView):
    column_list = [
        "id",
        "user_id",
        "district.name",
        "region.name",
        "is_event_organizer",
        "name",
        "age",
    ]
    column_searchable_list = [
        "name",
        "age",
        "user_id",
    ]
    column_filters = ["region.name", "district.name", "is_event_organizer"]
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "district.name": "Район",
        "region.name": "Регион",
        "is_event_organizer": "Хочет организовать мероприятия?",
        "name": "ФИО",
        "age": "Возраст",
    }
    column_sortable_list = ["name", "district.name", "region.name"]
