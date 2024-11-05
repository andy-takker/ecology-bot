import enum


class EventType(enum.StrEnum):
    """Типы событий"""

    DEFAULT = "DEFAULT"  # Обычное событие
    RECRUITMENT = "RECRUITMENT"  # Нужны волонтеры
