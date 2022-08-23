from ecology_bot.admin.app import create_app
from ecology_bot.utils.get_settings import get_settings

settings = get_settings()

app = create_app(
    config={
        "DEBUG": settings.DEBUG,
        "SQLALCHEMY_DATABASE_URI": settings.CELERY_DBURI,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSON_AS_ASCII": False,
        "SECRET_KEY": settings.SECRET_KEY,
    }
)
