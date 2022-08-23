from ecology_bot.admin.admin.models.view import SecureModelView


class DistrictModelView(SecureModelView):
    column_list = ['name', 'type', 'region']
    form_columns = ["name", "type", "region", "children", "invite_link"]
    column_searchable_list = ["name", "region.name"]
    column_labels = {
        "name": "Название района",
        "type": "Тип",
        "region": "Регион",
        "children": "Подрайоны",
        "invite_link": "Ссылка на чат",
    }
    column_sortable_list = ['name']