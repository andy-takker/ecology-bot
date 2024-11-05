from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    select,
)
from sqlalchemy import text as sa_text
from sqlalchemy.orm import (
    Mapped,
    Query,
    backref,
    mapped_column,
    relationship,
    selectinload,
)
from werkzeug.security import check_password_hash, generate_password_hash

from ecology_bot.adapters.database.base import Base, IdentifableMixin, TimestampedMixin
from ecology_bot.domains.entities.district import DistrictType
from ecology_bot.domains.entities.event import EventType


class Activity(IdentifableMixin, Base):
    """Экологические активности"""

    __tablename__ = "activities"

    __verbose_name__ = "Активность"
    __verbose_name_plural__ = "Активности"
    __admin_endpoint__ = "eco_activities"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

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

    def __str__(self) -> str:
        return self.name


class Region(IdentifableMixin, Base):
    """Регион"""

    __tablename__ = "regions"

    __verbose_name__ = "Регион"
    __verbose_name_plural__ = "Регионы"
    __admin_endpoint__ = "regions"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    profiles = relationship("Profile", back_populates="region")
    districts = relationship("District", back_populates="region")

    def __str__(self) -> str:
        return self.name


class District(IdentifableMixin, Base):
    """Район"""

    __tablename__ = "districts"

    __verbose_name__ = "Район"
    __verbose_name_plural__ = "Районы"
    __admin_endpoint__ = "districts"

    name: Mapped[str] = mapped_column(
        String(255), unique=False, nullable=False, index=True
    )
    type: Mapped[DistrictType] = mapped_column(
        String(255),
        default=DistrictType.DISTRICT,
        nullable=False,
        index=True,
    )
    region_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("regions.id"), index=True, nullable=False
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.id"), index=True, default=None, nullable=True
    )
    invite_link: Mapped[str] = mapped_column(String(255), nullable=True)

    children: Mapped[list["District"]] = relationship(
        "District",
        backref=backref("parent", remote_side="District.id"),
        uselist=True,
        cascade="all, delete",
    )
    profiles = relationship("Profile", back_populates="district")
    organization = relationship("Organization", back_populates="district")
    events = relationship("Event", back_populates="district")
    region = relationship("Region", back_populates="districts")

    def __str__(self) -> str:
        return f"{self.name}"


class User(IdentifableMixin, TimestampedMixin, Base):
    """Пользователи"""

    __tablename__ = "users"

    __verbose_name__ = "Пользователь"
    __verbose_name_plural__ = "Пользователи"
    __admin_endpoint__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization", back_populates="creator"
    )
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


class Profile(IdentifableMixin, TimestampedMixin, Base):
    """Профиль волонтера"""

    __tablename__ = "profiles"

    __verbose_name__ = "Профиль волонтера"
    __verbose_name_plural__ = "Профили волонтеров"
    __admin_endpoint__ = "profiles"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
        unique=True,
    )

    district_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("districts.id"),
        index=True,
        nullable=False,
    )
    region_id: Mapped[int] = mapped_column(
        ForeignKey("regions.id"), index=True, nullable=False
    )

    is_event_organizer: Mapped[bool] = mapped_column(Boolean, index=True, default=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)

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

    def __str__(self) -> str:
        """Профиль пользователя"""
        return f"Profile {self.id} ({self.user_id})"

    @property
    def info(self) -> str:
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


class Organization(IdentifableMixin, TimestampedMixin, Base):
    """Организации."""

    __tablename__ = "organizations"

    __verbose_name__ = "Организация"
    __verbose_name_plural__ = "Организации"
    __admin_endpoint__ = "organizations"

    creator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=False
    )
    district_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("districts.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    is_checked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superorganization: Mapped[bool] = mapped_column(Boolean, default=False)

    creator = relationship("User", back_populates="organizations")
    activities = relationship(
        "Activity",
        secondary="activity_organization",
        back_populates="organizations",
        cascade="all, delete",
    )
    district = relationship("District", back_populates="organization")
    events = relationship("Event", back_populates="organization")

    def __str__(self) -> str:
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
    def info(self) -> str:
        """Информация об организации."""
        name = f"Название: {self.name}\n\n"
        districts = f"Район: {self.district}\n"
        a = ", ".join([str(a) for a in self.activities])
        activities = f"Активности: {a}"
        return f"{name}{districts}{activities}"


class VolunteerType(IdentifableMixin, Base):
    """Виды волонтерской помощи."""

    __tablename__ = "volunteer_types"

    __verbose_name__ = "Вид волонтерской помощи"
    __verbose_name_plural__ = "Виды волонтерской помощи"
    __admin_endpoint__ = "volunteer_types"

    name: Mapped[str] = mapped_column(String(255), index=True)

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

    def __str__(self) -> str:
        """Название вида волонтеров."""
        return self.name


class ActivityOrganization(IdentifableMixin, Base):
    """Secondary table for activity and organization."""

    __tablename__ = "activity_organizations"

    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activities.id"),
        index=True,
        nullable=False,
    )
    organization_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class GlobalEvent(IdentifableMixin, TimestampedMixin, Base):
    __tablename__ = "global_events"

    __verbose_name__ = "Глобальное мероприятие"
    __verbose_name_plural__ = "Глобальные мероприятия"
    __admin_endpoint__ = "global_events"

    name: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(2048), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    users = relationship(
        "User", back_populates="global_events", secondary="global_event_user"
    )
    global_event_users = relationship(
        "GlobalEventUser", back_populates="global_event", viewonly=True
    )
    global_mailings = relationship("GlobalMailing", back_populates="global_event")

    def __str__(self):
        return self.name

    @property
    def clean_description(self):
        return self.description.replace("<p>", "").replace("</p>", "")


class GlobalEventUser(IdentifableMixin, TimestampedMixin, Base):
    __tablename__ = "global_event_users"

    __verbose_name__ = "Подписчик мероприятия"
    __verbose_name_plural__ = "Подписчики мероприятий"
    __admin_endpoint__ = "global_event_users"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "global_event_id", name="_user_id_global_event_id_uc"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), index=True, nullable=False
    )
    global_event_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("global_events.id"), index=True, nullable=False
    )
    is_subscribed: Mapped[bool] = mapped_column(Boolean, index=True, default=False)

    user = relationship("User", back_populates="global_event_users", viewonly=True)
    global_event = relationship(
        "GlobalEvent", back_populates="global_event_users", viewonly=True
    )


class Event(IdentifableMixin, TimestampedMixin, Base):
    """Событие"""

    __tablename__ = "events"

    __verbose_name__ = "Событие"
    __verbose_name_plural__ = "События"
    __admin_endpoint__ = "events"

    name: Mapped[str] = mapped_column(String(511), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(2047), nullable=False)
    type: Mapped[EventType] = mapped_column(String(255), index=True, nullable=False)
    organization_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("organizations.id"),
        index=True,
        nullable=False,
    )
    district_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("districts.id"),
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

    def __str__(self) -> str:
        return self.name

    @property
    def message(self) -> str:
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


class VolunteerTypeEvent(IdentifableMixin, Base):
    """Secondary table for volunteer type and event."""

    __tablename__ = "volunteer_type_events"

    volunteer_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("volunteer_types.id"),
        index=True,
        nullable=False,
    )
    event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class VolunteerTypeProfile(IdentifableMixin, Base):
    """Secondary table for volunteer_type and Profile."""

    __tablename__ = "volunteer_type_profiles"

    volunteer_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("volunteer_types.id"),
        index=True,
        nullable=False,
    )
    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class ActivityEvent(IdentifableMixin, Base):
    """Secondary table for activity and event."""

    __tablename__ = "activity_events"

    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activities.id"),
        index=True,
        nullable=False,
    )
    event_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("events.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )


class GlobalMailing(IdentifableMixin, TimestampedMixin, Base):
    """Глобальная рассылка пользователей"""

    __tablename__ = "global_mailings"

    __verbose_name__ = "Глобальная рассылка"
    __verbose_name_plural__ = "Глобальные рассылки"
    __admin_endpoint__ = "global_mailings"

    name: Mapped[str] = mapped_column(String(511), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(3071), index=True, nullable=False)
    global_event_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("global_events.id"), index=True, nullable=False
    )

    global_event = relationship("GlobalEvent", back_populates="global_mailings")

    @property
    def clean_description(self):
        return self.description.replace("<p>", "").replace("</p>", "")


class Mailing(IdentifableMixin, TimestampedMixin, Base):
    """Рассылка."""

    __tablename__ = "mailings"

    __verbose_name__ = "Рассылка"
    __verbose_name_plural__ = "Рассылки"

    is_executed: Mapped[bool] = mapped_column(Boolean, index=True, default=False)
    start_execute_datetime: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    end_execute_datetime: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    event_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("events.id"), index=True, nullable=False
    )

    event = relationship("Event", back_populates="mailing", uselist=False)

    def __str__(self) -> str:
        """Return Mailing name."""
        return f"{self.id} Mailing (executed: {self.is_executed})"


class ActivityProfile(IdentifableMixin, Base):
    """Secondary table for activity and profile."""

    __tablename__ = "activity_profiles"

    profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    activity_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("activities.id"),
        index=True,
        nullable=False,
    )


class Employee(Base, IdentifableMixin, TimestampedMixin, UserMixin):
    """Сотрудник админки."""

    __tablename__ = "employees"

    __verbose_name__ = "Аккаунт сотрудника"
    __verbose_name_plural__ = "Аккаунты сотрудников"

    login: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    def get_id(self) -> int:
        """Возвращает идентификатор."""
        return self.id

    def check_password(self, password: str) -> bool:
        """Проверяет пароль сотрудника."""
        return check_password_hash(self.password_hash, password)

    def set_password(self, password: str) -> None:
        """Назначает пароль сотруднику."""
        self.password_hash = generate_password_hash(password)


class TextChunk(Base, IdentifableMixin, TimestampedMixin):
    __tablename__ = "text_chunks"

    __verbose_name__ = "Текст сообщения"
    __verbose_name_plural__ = "Тексты сообщений"
    __admin_endpoint__ = "text_chunks"
    __table_args__ = (UniqueConstraint("key", "weight", name="_key_weight_uc"),)

    key: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    text: Mapped[str] = mapped_column(String, nullable=False, default="")
    weight: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=sa_text("0")
    )

    def __repr__(self) -> str:
        return f"TextChunk ({self.id} {self.key})"

    def __str__(self) -> str:
        return f"Text: {self.text}"


class AwesomeData(Base, IdentifableMixin, TimestampedMixin):
    __tablename__ = "awesome_datas"

    __verbose_name__ = "Данные от пользователя"
    __verbose_name_plural__ = "Данные от пользователя"
    __admin_endpoint__ = "awesome_data"

    from_user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    data: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f"AwesomeData: ({self.id})"
