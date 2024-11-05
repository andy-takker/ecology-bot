from flask import request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import redirect

__all__ = [
    "SecureModelView",
]


class SecureModelView(ModelView):
    can_export = True
    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("login.index", next=request.endpoint))
