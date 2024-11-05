from flask_login import LoginManager

from ecology_bot.adapters.database.models import Employee
from ecology_bot.database.engine import get_admin_db


def get_login_manager():
    db = get_admin_db()
    login = LoginManager()
    login.user_loader(lambda user_id: db.session.query(Employee).get(user_id))
    return login
