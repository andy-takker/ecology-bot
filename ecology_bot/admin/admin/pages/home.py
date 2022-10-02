from flask_admin import AdminIndexView, expose


class HomeAdminIndexView(AdminIndexView):
    """Главная страница"""

    @expose('/')
    def index(self):
        return self.render(template='admin_panel/home.html')
