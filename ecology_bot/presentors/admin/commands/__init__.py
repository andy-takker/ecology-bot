from flask import Flask

from ecology_bot.admin.commands.database import db_commands


def register_commands(flask_app: Flask):
    for command in [db_commands]:
        flask_app.cli.add_command(command)
