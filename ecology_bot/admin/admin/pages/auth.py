import datetime
import logging
from string import digits, ascii_lowercase

from flask import request, flash, redirect, url_for, Response, current_app
from flask_admin import BaseView, expose
from flask_admin.menu import MenuLink
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.routing import BuildError
from wtforms import (
    StringField,
    validators,
    PasswordField,
    BooleanField,
    ValidationError,
    SubmitField,
)

from ecology_bot.database.engine import get_admin_db
from ecology_bot.database.models import Employee

logger = logging.getLogger(__name__)

alphabet = digits + ascii_lowercase + "_"

db = get_admin_db()


class LoginLink(MenuLink):
    def is_visible(self) -> bool:
        return not current_user.is_authenticated

    def is_accessible(self) -> bool:
        return not current_user.is_authenticated

    def get_url(self) -> str:
        return url_for("login.index")


class LogoutLink(MenuLink):
    def is_visible(self) -> bool:
        return current_user.is_authenticated

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

    def get_url(self) -> str:
        return url_for("login.logout")


class LoginForm(FlaskForm):
    login = StringField(
        label="Login",
        validators=[validators.DataRequired()],
        description="Username",
    )
    password = PasswordField(
        label="Password",
        validators=[validators.DataRequired()],
        description="Password from account",
    )
    remember = BooleanField(label="Remember session")

    submit = SubmitField(label="Login")

    class Meta:
        csrf = True

    def validate_login(self, field: StringField) -> None:
        if any(filter(lambda i: i not in alphabet, field.data)):
            raise ValidationError("Login is incorrect! ")


def redirect_dest(fallback) -> Response:
    dest = request.args.get("next")
    try:
        dest_url = url_for(dest)
        return redirect(dest_url)
    except (BuildError, TypeError):
        return redirect(fallback)


class LoginView(BaseView):
    def is_visible(self) -> bool:
        return False

    @expose("/", methods=("GET", "POST"))
    def index(self):

        if current_user.is_authenticated:
            logger.info("logined")
        form = LoginForm(request.form)
        if request.method == "POST" and form.validate_on_submit():
            employee = (
                db.session.query(Employee).filter_by(login=form.login.data).first()
            )
            logger.info(employee)
            logger.info(form.password.data)
            if not employee or not employee.check_password(password=form.password.data):
                flash("Wrong login data!")
                return self.render("admin_panel/login.html", form=form)
            login_user(
                employee,
                remember=form.remember.data,
                duration=datetime.timedelta(days=30),
            )
            return redirect_dest(fallback=url_for("admin.index"))
        return self.render("admin_panel/login.html", form=form)

    @expose("/logout")
    def logout(self):
        current_app.logger.info("Logout")
        logout_user()
        flash("Logout")
        return redirect(url_for("login.index"))
