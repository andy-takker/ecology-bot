from celery import Celery

from ecology_bot.utils.get_settings import get_settings


def get_celery_application():
    settings = get_settings()
    app = Celery(__name__)
    app.config_from_object(
        {
            "broker_url": settings.REDIS_URI,
            "result_backend": "db+" + settings.CELERY_DBURI,
            "result_extended": True,
            "task_track_started": True,
            "timezone": "Europe/Moscow",
            "beat_dburi": settings.CELERY_DBURI,
            "include": ["ecology_bot.workers.mailing"],
            "worker_max_tasks_per_child": 100,
        }
    )
    return app


celery = get_celery_application()
