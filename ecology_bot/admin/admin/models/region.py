from ecology_bot.admin.admin.view import SecureModelView


class RegionModelView(SecureModelView):
    column_list = ["name"]

    column_labels = {
        "name": "Название",
    }
    column_searchable_list = ["name"]
    column_sortable_list = ["name"]
