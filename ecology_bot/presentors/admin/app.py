import logging

from flask import Flask
from redis import Redis

from ecology_bot.adapters.database.models import Activity, Employee, Event, Organization
from ecology_bot.admin.admin.admin_conf import register_admin
from ecology_bot.admin.commands import register_commands
from ecology_bot.admin.utils.login_manager import get_login_manager
from ecology_bot.config import DefaultSettings
from ecology_bot.database.engine import get_admin_db


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


def create_app(settings: DefaultSettings) -> Flask:
    """Фабрика приложений"""
    config = {
        "DEBUG": settings.DEBUG,
        "SQLALCHEMY_DATABASE_URI": settings.CELERY_DBURI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSON_AS_ASCII": False,
        "SECRET_KEY": settings.SECRET_KEY,
    }
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
    redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_CACHE_DB,
    )

    flask_app.extensions["redis"] = redis
    return flask_app
