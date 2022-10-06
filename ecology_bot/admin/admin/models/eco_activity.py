from ecology_bot.admin.admin.view import SecureModelView


class EcoActivityModelView(SecureModelView):
    column_labels = {"name": "Название"}
    form_columns = ["name"]
