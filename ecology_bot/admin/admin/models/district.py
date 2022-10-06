from ecology_bot.admin.admin.view import SecureModelView


class DistrictModelView(SecureModelView):
    column_list = ["name", "type", "region", "children"]
    form_columns = ["name", "type", "region", "parent", "invite_link"]
    column_searchable_list = [
        "name",
        "region.name",
    ]
    column_labels = {
        "name": "Название района",
        "type": "Тип",
        "region": "Регион",
        "parent": "Надрайон",
        "children": "Внутренние",
        "invite_link": "Ссылка на чат",
    }
    column_sortable_list = ["name"]
