from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, MetaData, text
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declarative_mixin,
    declared_attr,
    mapped_column,
)

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()],
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)  # type: ignore[arg-type]

    def update(self, data: dict):
        for field in self.__table__.columns:
            if field.name in data:
                setattr(self, field.name, data[field.name])


@declarative_mixin
class TimestampedMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=text("TIMEZONE('utc', now())"),
            server_onupdate=text("TIMEZONE('utc', now())"),
            onupdate=now_with_tz,
        )


@declarative_mixin
class IdentifableMixin:
    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        )


def now_with_tz() -> datetime:
    return datetime.now(tz=UTC)
