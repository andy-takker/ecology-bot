from ecology_bot.admin.admin.view import SecureModelView


class ActivityModelView(SecureModelView):
    column_labels = {"name": "Название"}
    form_columns = ["name"]
