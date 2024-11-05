from ecology_bot.admin.admin.view import SecureModelView


class GlobalEventUserModelView(SecureModelView):
    column_list = [
        "created_at",
        "updated_at",
        "global_event.name",
        "user.telegram_id",
        "is_subscribed",
    ]
    column_labels = {
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "global_event.name": "Глобальное событие",
        "user.telegram_id": "Пользователь",
        "is_subscribed": "Подписан?",
    }
    column_filters = ["global_event.name", "created_at", "is_subscribed"]
    can_create = False
    column_sortable_list = [
        "created_at",
        "updated_at",
        "global_event.name",
        "user.telegram_id",
        "is_subscribed",
    ]
