import logging
import sys

import click
from flask.cli import AppGroup, with_appcontext

from ecology_bot.adapters.database.models import Employee
from ecology_bot.database.engine import get_admin_db

logger = logging.getLogger(__name__)

db_commands = AppGroup("bot-db")


@db_commands.command("create-user")
@click.option(
    "--login",
    "-l",
    required=True,
    help="Логин для нового пользователя. Должен быть уникальным",
)
@click.option(
    "--password",
    "-p",
    required=True,
    help="Пароль нового пользователя. Должен быть надежным.",
)
@with_appcontext
def create_user(login: str, password: str) -> None:
    db = get_admin_db()
    e = db.session.query(Employee).filter_by(login=login).first()
    if e is not None:
        logger.error("Такой логин уже занят!!!")
        sys.exit(128)

    e = Employee()
    e.login = login
    e.set_password(password=password)
    db.session.add(e)
    db.session.commit()
    logger.info("Пользователь создан!")
    sys.exit(0)
