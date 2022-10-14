from ecology_bot.admin.app import create_app
from ecology_bot.utils.get_settings import get_settings

settings = get_settings()

app = create_app(settings=settings)
