import enum
from typing import List

from flask_login import UserMixin
from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    String,
    Boolean,
    DateTime,
    Integer,
    UniqueConstraint,
    text as sa_text,
)
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, backref, selectinload, Query
from sqlalchemy_utils import ChoiceType
from werkzeug.security import check_password_hash, generate_password_hash

from ecology_bot.database.base import Base
from ecology_bot.database.mixins import PkMixin, TimestampMixin

__all__ = [
    "Activity",
    "ActivityEvent",
    "ActivityOrganization",
    "ActivityProfile",
    "AwesomeData",
    "District",
    "DistrictType",
    "Employee",
    "Event",
    "EventType",
    "GlobalEvent",
    "GlobalEventUser",
    "Mailing",
    "Organization",
    "Profile",
    "Region",
    "TextChunk",
    "User",
    "VolunteerType",
    "VolunteerTypeEvent",
    "VolunteerTypeProfile",
]


class EventType(enum.Enum):
    """Типы событий"""

    DEFAULT = "DEFAULT"  # Обычное событие
    RECRUITMENT = "RECRUITMENT"  # Нужны волонтеры


class DistrictType(enum.Enum):
    """Типы территориальных образований"""

    DISTRICT = "DISTRICT"
    MUNICIPAL = "MUNICIPAL"


class Activity(PkMixin, Base):
    """Экологические активности"""

    __verbose_name__ = "Активность"
    __verbose_name_plural__ = "Активности"
    __admin_endpoint__ = "eco_activities"

    name = Column(String, unique=True, nullable=False, index=True)

    organizations = relationship(
        "Organization",
        secondary="activity_organization",
        back_populates="activities",
    )

    events = relationship(
        "Event", secondary="activity_event", back_populates="activities"
    )
    profiles = relationship(
        "Profile", secondary="activity_profile", back_populates="activities"
    )

    def __str__(self):
        return self.name


class Region(PkMixin, Base):
    """Регион"""

    __verbose_name__ = "Регион"
    __verbose_name_plural__ = "Регионы"
    __admin_endpoint__ = "regions"

    name = Column(String(255), unique=True, nullable=False, index=True)

    profiles = relationship("Profile", back_populates="region")
    districts = relationship("District", back_populates="region")

    def __str__(self):
        return self.name


class District(PkMixin, Base):
    """Район"""

    __verbose_name__ = "Район"
    __verbose_name_plural__ = "Районы"
    __admin_endpoint__ = "districts"

    name = Column(String(255), unique=False, nullable=False, index=True)
    type = Column(
        ChoiceType(DistrictType, impl=String(255)),
        default=DistrictType.DISTRICT,
        nullable=False,
        index=True,
    )
    region_id = Column(BigInteger, ForeignKey("region.id"), index=True, nullable=False)
    parent_id = Column(
        BigInteger, ForeignKey("district.id"), index=True, default=None, nullable=True
    )
    invite_link = Column(String(255), nullable=True)

    children: list["District"] = relationship(
        "District",
        backref=backref("parent", remote_side="District.id"),
        uselist=True,
        cascade="all, delete",
    )
    profiles = relationship("Profile", back_populates="district")
    organization = relationship("Organization", back_populates="district")
    events = relationship("Event", back_populates="district")
    region = relationship("Region", back_populates="districts")

    def __str__(self):
        return f"{self.name}"


class User(PkMixin, TimestampMixin, Base):
    """Пользователи"""

    __verbose_name__ = "Пользователь"
    __verbose_name_plural__ = "Пользователи"
    __admin_endpoint__ = "users"

    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False)

    organizations: List = relationship("Organization", back_populates="creator")
    profile = relationship("Profile", back_populates="user", uselist=False)
    global_events = relationship(
        "GlobalEvent", secondary="global_event_user", back_populates="users"
    )
    global_event_users = relationship(
        "GlobalEventUser", back_populates="user", viewonly=True
    )

    @property
    def has_unchecked_organizations(self) -> bool:
        return any(
            map(lambda organization: not organization.is_checked, self.organizations)
        )

    @property
    def has_checked_organizations(self) -> bool:
        return any(
            map(lambda organization: organization.is_checked, self.organizations)
        )

    def __str__(self) -> str:
        return f"User ({self.telegram_id})"


class Profile(PkMixin, TimestampMixin, Base):
    """Профиль волонтера"""

    __verbose_name__ = "Профиль волонтера"
    __verbose_name_plural__ = "Профили волонтеров"
    __admin_endpoint__ = "profiles"

    user_id = Column(
        BigInteger,
        ForeignKey("user.id"),
        index=True,
        nullable=False,
        unique=True,
    )

    district_id = Column(
        BigInteger,
        ForeignKey("district.id"),
        index=True,
        nullable=False,
    )
    region_id = Column(ForeignKey("region.id"), index=True, nullable=False)

    is_event_organizer = Column(Boolean, index=True, default=False)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)

    user = relationship("User", back_populates="profile", uselist=False)
    region = relationship("Region", back_populates="profiles")

    activities = relationship(
        "Activity",
        secondary="activity_profile",
        back_populates="profiles",
    )
    volunteer_types = relationship(
        "VolunteerType",
        secondary="volunteer_type_profile",
        back_populates="profiles",
    )
    district = relationship("District", back_populates="profiles")

    def __str__(self: "Profile") -> str:
        """Профиль пользователя"""
        return f"Profile {self.id} ({self.user_id})"

    @property
    def info(self: "Profile") -> str:
        activities = ", ".join(e.name for e in self.activities)
        msg = (
            f"Регион: {self.region}\n"
            f"Район: {self.district}\n\n"
            f"Активности: \n{activities}"
        )
        if self.is_event_organizer:
            volunteer_types = ", ".join(v.name for v in self.volunteer_types)
            msg += (
                "\n\nТы также подписан(а) на сообщения об организации "
                "мероприятий.\n"
                f"Имя: {self.name}\nВозраст: {self.age}\n"
                f"Виды помощи, которые ты указал(а):"
                f"\n{volunteer_types}"
            )
        return msg

    @classmethod
    def q_from_telegram_id(cls: "Profile", telegram_id: int) -> Query:
        """Запрос с пользователем по telegram_id"""
        return (
            select(cls)
            .join(User, User.id == Profile.user_id)
            .filter(User.telegram_id == telegram_id)
        )


class Organization(PkMixin, TimestampMixin, Base):
    """Организации."""

    __verbose_name__ = "Организация"
    __verbose_name_plural__ = "Организации"
    __admin_endpoint__ = "organizations"

    creator_id = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)
    district_id = Column(
        BigInteger, ForeignKey("district.id"), index=True, nullable=False
    )
    name = Column(String, index=True)
    is_checked = Column(Boolean, default=False)
    is_superorganization = Column(Boolean, default=False)

    creator = relationship("User", back_populates="organizations")
    activities = relationship(
        "Activity",
        secondary="activity_organization",
        back_populates="organizations",
        cascade="all, delete",
    )
    district = relationship("District", back_populates="organization")
    events = relationship("Event", back_populates="organization")

    def __str__(self: "Organization") -> str:
        """Название организации."""
        return self.name

    @classmethod
    def query(cls) -> Query:
        return select(Organization).options(
            selectinload(Organization.creator),
            selectinload(Organization.district),
            selectinload(Organization.activities),
            selectinload(Organization.events),
        )

    @property
    def info(self: "Organization") -> str:
        """Информация об организации."""
        name = f"Название: {self.name}\n\n"
        districts = f"Район: {self.district}\n"
        a = ", ".join([str(a) for a in self.activities])
        activities = f"Активности: {a}"
        return f"{name}{districts}{activities}"


class VolunteerType(PkMixin, Base):
    """Виды волонтерской помощи."""

    __verbose_name__ = "Вид волонтерской помощи"
    __verbose_name_plural__ = "Виды волонтерской помощи"
    __admin_endpoint__ = "volunteer_types"

    name = Column(String, index=True)

    events = relationship(
        "Event",
        secondary="volunteer_type_event",
        back_populates="volunteer_types",
    )
    profiles = relationship(
        "Profile",
        secondary="volunteer_type_profile",
        back_populates="volunteer_types",
    )

    def __str__(self: "VolunteerType") -> str:
        """Название вида волонтеров."""
        return self.name


class ActivityOrganization(PkMixin, Base):
    """Secondary table for activity and organization."""

    activity_id = Column(
        BigInteger,
        ForeignKey("activity.id"),
        index=True,
        nullable=False,
    )
    organization_id = Column(
        BigInteger,
        ForeignKey("organization.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class GlobalEvent(PkMixin, TimestampMixin, Base):
    __verbose_name__ = "Глобальное событие"
    __verbose_name_plural__ = "Глобальные события"
    __admin_endpoint__ = "global_events"

    name = Column(String(512), index=True, nullable=False)
    description = Column(String(3072), index=True, nullable=False)
    is_active = Column(Boolean, default=False)

    users = relationship(
        "User", back_populates="global_events", secondary="global_event_user"
    )
    global_event_users = relationship(
        "GlobalEventUser", back_populates="global_event", viewonly=True
    )

    def __str__(self):
        return self.name

    @property
    def clean_description(self):
        return self.description.replace("<p>", "").replace("</p>", "")


class GlobalEventUser(PkMixin, TimestampMixin, Base):
    __verbose_name__ = "Подписчик глобального события"
    __verbose_name_plural__ = "Подписчики глобальных событий"
    __admin_endpoint__ = "global_event_users"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "global_event_id", name="_user_id_global_event_id_uc"
        ),
    )

    user_id = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)
    global_event_id = Column(
        BigInteger, ForeignKey("global_event.id"), index=True, nullable=False
    )
    is_subscribed = Column(Boolean, index=True, default=False)

    user = relationship("User", back_populates="global_event_users", viewonly=True)
    global_event = relationship(
        "GlobalEvent", back_populates="global_event_users", viewonly=True
    )


class Event(PkMixin, TimestampMixin, Base):
    """Событие"""

    __verbose_name__ = "Событие"
    __verbose_name_plural__ = "События"
    __admin_endpoint__ = "events"

    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    type = Column(ChoiceType(EventType, impl=String(255)), index=True, nullable=False)
    organization_id = Column(
        BigInteger,
        ForeignKey("organization.id"),
        index=True,
        nullable=False,
    )
    district_id = Column(
        BigInteger,
        ForeignKey("district.id"),
        index=True,
        nullable=False,
    )
    mailing = relationship("Mailing", back_populates="event", uselist=False)
    organization = relationship("Organization", back_populates="events")

    district = relationship("District", back_populates="events")

    activities = relationship(
        "Activity",
        secondary="activity_event",
        back_populates="events",
    )

    volunteer_types = relationship(
        "VolunteerType",
        secondary="volunteer_type_event",
        back_populates="events",
    )

    def __str__(self: "Event") -> str:
        """Название мероприятия."""
        return self.name

    @property
    def message(self: "Event") -> str:
        """Сообщение о мероприятии."""
        if self.type == EventType.DEFAULT:
            activities = ", ".join(a.name for a in self.activities).lower()
            return (
                f"В районе {self.district} проходит мероприятие <i>"
                f'"{self.name}"</i>\nОно относится к активностям: '
                f"{activities}"
                f"\n\nОписание:\n{self.description} \n\n"
                f'Его проводит организация <b>"{self.organization}"</b>'
            )
        elif self.type == EventType.RECRUITMENT:
            volunteer_types = ", ".join(v.name for v in self.volunteer_types)
            return (
                f'<i>"{self.name}"</i>\n'
                f'Организации <b>"{self.organization}"</b> нужны: {volunteer_types}'
                f" волонтеры в МО "
                f"<b>{self.district}</b>\n\nОписание:\n{self.description}"
            )
        return ""

    @classmethod
    def query(cls: "Event") -> Query:
        """Return full query for class."""
        return select(cls).options(
            selectinload(cls.district),
            selectinload(cls.activities),
            selectinload(cls.volunteer_types),
            selectinload(cls.organization),
        )


class VolunteerTypeEvent(PkMixin, Base):
    """Secondary table for volunteer type and event."""

    volunteer_type_id = Column(
        BigInteger,
        ForeignKey("volunteer_type.id"),
        index=True,
        nullable=False,
    )
    event_id = Column(
        BigInteger,
        ForeignKey("event.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class VolunteerTypeProfile(PkMixin, Base):
    """Secondary table for volunteer_type and Profile."""

    volunteer_type_id = Column(
        BigInteger,
        ForeignKey("volunteer_type.id"),
        index=True,
        nullable=False,
    )
    profile_id = Column(
        BigInteger,
        ForeignKey("profile.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class ActivityEvent(PkMixin, Base):
    """Secondary table for activity and event."""

    activity_id = Column(
        BigInteger,
        ForeignKey("activity.id"),
        index=True,
        nullable=False,
    )
    event_id = Column(
        BigInteger,
        ForeignKey("event.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class Mailing(PkMixin, TimestampMixin, Base):
    """Рассылка."""

    __verbose_name__ = "Рассылка"
    __verbose_name_plural__ = "Рассылки"

    is_executed = Column(Boolean, index=True, default=False)
    start_execute_datetime = Column(DateTime, nullable=True, index=True)
    end_execute_datetime = Column(DateTime, nullable=True, index=True)
    event_id = Column(BigInteger, ForeignKey("event.id"), index=True, nullable=False)

    event = relationship("Event", back_populates="mailing", uselist=False)

    def __str__(self: "Mailing") -> str:
        """Return Mailing name."""
        return f"{self.id} Mailing (executed: {self.is_executed})"


class ActivityProfile(PkMixin, Base):
    """Secondary table for activity and profile."""

    profile_id = Column(
        BigInteger,
        ForeignKey("profile.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    activity_id = Column(
        BigInteger,
        ForeignKey("activity.id"),
        index=True,
        nullable=False,
    )


class Employee(Base, PkMixin, TimestampMixin, UserMixin):
    """Сотрудник админки."""

    __verbose_name__ = "Аккаунт сотрудника"
    __verbose_name_plural__ = "Аккаунты сотрудников"

    login = Column(String(30), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def get_id(self: "Employee") -> int:
        """Возвращает идентификатор."""
        return self.id

    def check_password(self: "Employee", password: str) -> bool:
        """Проверяет пароль сотрудника."""
        return check_password_hash(self.password_hash, password)

    def set_password(self: "Employee", password: str) -> None:
        """Назначает пароль сотруднику."""
        self.password_hash = generate_password_hash(password)


class TextChunk(Base, PkMixin, TimestampMixin):
    __verbose_name__ = "Текст сообщения"
    __verbose_name_plural__ = "Тексты сообщений"
    __admin_endpoint__ = "text_chunks"
    __table_args__ = (UniqueConstraint("key", "weight", name="_key_weight_uc"),)
    key = Column(String(64), nullable=False)
    description = Column(String(512), nullable=False, default="")
    text = Column(String, nullable=False, default="")
    weight = Column(Integer, nullable=False, default=0, server_default=sa_text("0"))

    def __repr__(self):
        return f"TextChunk ({self.id} {self.key})"

    def __str__(self: "TextChunk"):
        return f"Text: {self.text}"


class AwesomeData(Base, PkMixin, TimestampMixin):
    __verbose_name__ = "Данные от пользователя"
    __verbose_name_plural__ = "Данные от пользователя"
    __admin_endpoint__ = "awesome_data"

    from_user_id = Column(BigInteger, nullable=True)
    description = Column(String(512), nullable=False, default="")
    data = Column(String, nullable=False)

    def __repr__(self):
        return f"AwesomeData: ({self.id})"
