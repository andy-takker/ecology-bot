from ecology_bot.admin.admin.view import SecureModelView

__all__ = [
    "VolunteerTypeModelView",
]


class VolunteerTypeModelView(SecureModelView):
    form_columns = ["name"]
    column_labels = {"name": "Название"}
    column_default_sort = "name"
