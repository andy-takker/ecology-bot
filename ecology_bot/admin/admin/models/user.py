from ecology_bot.admin.admin.models.view import SecureModelView


class UserModelView(SecureModelView):
    column_list = ['created_at', 'updated_at', 'telegram_id', 'is_admin', 'organizations', 'profile']
    form_columns = ["telegram_id","is_admin"]
    column_searchable_list = ["telegram_id", "is_admin"]
    column_labels = {
        "created_at": "Создано",
        "updated_at": "Обновлено",
        "telegram_id": "Telegram ID",
        "is_admin": "Является администратором?",
        "organizations": "Организации",
        "profile": "Профиль"
    }
    column_sortable_list = ['telegram_id']