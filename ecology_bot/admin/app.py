import logging
from typing import Any

from flask import Flask

from ecology_bot.admin.utils.login_manager import get_login_manager
from ecology_bot.admin.admin.admin_conf import register_admin
from ecology_bot.admin.commands import register_commands
from ecology_bot.database.engine import get_admin_db
from ecology_bot.database.models import Employee, Event, Organization, Activity


def register_shell_context(flask_app: Flask) -> None:
    """Добавляем в контекст приложения нужные переменные"""

    def shell_context():
        db = get_admin_db()
        return {
            "db": db,
            "Activity": Activity,
            "Employee": Employee,
            "Event": Event,
            "Organization": Organization,
        }

    flask_app.shell_context_processor(shell_context)


def create_app(config: dict[str, Any]) -> Flask:
    """Фабрика приложений"""
    logging.basicConfig(level=logging.INFO)
    db = get_admin_db()
    flask_app = Flask(
        __name__,
        static_url_path="",
        static_folder="frontend/static",
        template_folder="frontend/templates",
    )
    flask_app.config.update(**config)
    register_admin(flask_app=flask_app, database=db)
    register_shell_context(flask_app)
    register_commands(flask_app)
    login_manager = get_login_manager()
    login_manager.init_app(flask_app)
    db.init_app(app=flask_app)
    return flask_app
