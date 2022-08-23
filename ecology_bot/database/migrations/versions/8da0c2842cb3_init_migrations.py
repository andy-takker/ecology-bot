"""Init migrations.

Revision ID: 8da0c2842cb3
Revises:
Create Date: 2022-07-24 20:51:02.178243

"""
from alembic import op
import sqlalchemy as sa

import sqlalchemy_utils

from ecology_bot.database import DistrictType, EventType

revision = "8da0c2842cb3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Обновление базы данных на версию 8da0c2842cb3."""
    op.create_table(
        "activity",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_activity_id"), "activity", ["id"], unique=False)
    op.create_index(op.f("ix_activity_name"), "activity", ["name"], unique=True)
    op.create_table(
        "employee",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("login", sa.String(length=30), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_id"), "employee", ["id"], unique=False)
    op.create_table(
        "region",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_region_id"), "region", ["id"], unique=False)
    op.create_index(op.f("ix_region_name"), "region", ["name"], unique=True)
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_user_telegram_id"), "user", ["telegram_id"], unique=True)
    op.create_table(
        "volunteer_type",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_volunteer_type_id"),
        "volunteer_type",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volunteer_type_name"),
        "volunteer_type",
        ["name"],
        unique=False,
    )
    op.create_table(
        "district",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sqlalchemy_utils.types.choice.ChoiceType(
                DistrictType,
                impl=sa.String(length=255),
            ),
            nullable=False,
        ),
        sa.Column("region_id", sa.BigInteger(), nullable=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("invite_link", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["district.id"],
        ),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["region.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_district_id"), "district", ["id"], unique=False)
    op.create_index(op.f("ix_district_name"), "district", ["name"], unique=False)
    op.create_index(
        op.f("ix_district_parent_id"),
        "district",
        ["parent_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_district_region_id"),
        "district",
        ["region_id"],
        unique=False,
    )
    op.create_index(op.f("ix_district_type"), "district", ["type"], unique=False)
    op.create_table(
        "organization",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("creator_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("is_checked", sa.Boolean(), nullable=True),
        sa.Column("is_superorganization", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organization_creator_id"),
        "organization",
        ["creator_id"],
        unique=False,
    )
    op.create_index(op.f("ix_organization_id"), "organization", ["id"], unique=False)
    op.create_index(
        op.f("ix_organization_name"),
        "organization",
        ["name"],
        unique=False,
    )
    op.create_table(
        "activity_organization",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("activity_id", sa.BigInteger(), nullable=False),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_activity_organization_activity_id"),
        "activity_organization",
        ["activity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_organization_id"),
        "activity_organization",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_organization_organization_id"),
        "activity_organization",
        ["organization_id"],
        unique=False,
    )
    op.create_table(
        "district_organization",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("district_id", sa.BigInteger(), nullable=False),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["district_id"],
            ["district.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_district_organization_district_id"),
        "district_organization",
        ["district_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_district_organization_id"),
        "district_organization",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_district_organization_organization_id"),
        "district_organization",
        ["organization_id"],
        unique=False,
    )
    op.create_table(
        "event",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column(
            "type",
            sqlalchemy_utils.types.choice.ChoiceType(
                EventType,
                impl=sa.String(length=255),
            ),
            nullable=True,
        ),
        sa.Column("organization_id", sa.BigInteger(), nullable=False),
        sa.Column("district_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["district_id"],
            ["district.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_event_district_id"),
        "event",
        ["district_id"],
        unique=False,
    )
    op.create_index(op.f("ix_event_id"), "event", ["id"], unique=False)
    op.create_index(op.f("ix_event_name"), "event", ["name"], unique=False)
    op.create_index(
        op.f("ix_event_organization_id"),
        "event",
        ["organization_id"],
        unique=False,
    )
    op.create_index(op.f("ix_event_type"), "event", ["type"], unique=False)
    op.create_table(
        "profile",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("district_id", sa.BigInteger(), nullable=False),
        sa.Column("region_id", sa.BigInteger(), nullable=False),
        sa.Column("is_event_organizer", sa.Boolean(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["district_id"],
            ["district.id"],
        ),
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["region.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_profile_district_id"),
        "profile",
        ["district_id"],
        unique=False,
    )
    op.create_index(op.f("ix_profile_id"), "profile", ["id"], unique=False)
    op.create_index(
        op.f("ix_profile_is_event_organizer"),
        "profile",
        ["is_event_organizer"],
        unique=False,
    )
    op.create_index(
        op.f("ix_profile_region_id"),
        "profile",
        ["region_id"],
        unique=False,
    )
    op.create_index(op.f("ix_profile_user_id"), "profile", ["user_id"], unique=True)
    op.create_table(
        "activity_event",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("activity_id", sa.BigInteger(), nullable=False),
        sa.Column("event_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_activity_event_activity_id"),
        "activity_event",
        ["activity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_event_event_id"),
        "activity_event",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_event_id"),
        "activity_event",
        ["id"],
        unique=False,
    )
    op.create_table(
        "activity_profile",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("profile_id", sa.BigInteger(), nullable=False),
        sa.Column("activity_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity.id"],
        ),
        sa.ForeignKeyConstraint(["profile_id"], ["profile.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_activity_profile_activity_id"),
        "activity_profile",
        ["activity_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_profile_id"),
        "activity_profile",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_activity_profile_profile_id"),
        "activity_profile",
        ["profile_id"],
        unique=False,
    )
    op.create_table(
        "mailing",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_executed", sa.Boolean(), nullable=True),
        sa.Column("start_execute_datetime", sa.DateTime(), nullable=True),
        sa.Column("end_execute_datetime", sa.DateTime(), nullable=True),
        sa.Column("event_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mailing_end_execute_datetime"),
        "mailing",
        ["end_execute_datetime"],
        unique=False,
    )
    op.create_index(op.f("ix_mailing_event_id"), "mailing", ["event_id"], unique=False)
    op.create_index(op.f("ix_mailing_id"), "mailing", ["id"], unique=False)
    op.create_index(
        op.f("ix_mailing_is_executed"),
        "mailing",
        ["is_executed"],
        unique=False,
    )
    op.create_index(
        op.f("ix_mailing_start_execute_datetime"),
        "mailing",
        ["start_execute_datetime"],
        unique=False,
    )
    op.create_table(
        "volunteer_type_event",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("volunteer_type_id", sa.BigInteger(), nullable=False),
        sa.Column("event_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.id"],
        ),
        sa.ForeignKeyConstraint(
            ["volunteer_type_id"],
            ["volunteer_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_volunteer_type_event_event_id"),
        "volunteer_type_event",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volunteer_type_event_id"),
        "volunteer_type_event",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volunteer_type_event_volunteer_type_id"),
        "volunteer_type_event",
        ["volunteer_type_id"],
        unique=False,
    )
    op.create_table(
        "volunteer_type_profile",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("volunteer_type_id", sa.BigInteger(), nullable=False),
        sa.Column("profile_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profile_id"],
            ["profile.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["volunteer_type_id"],
            ["volunteer_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_volunteer_type_profile_id"),
        "volunteer_type_profile",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volunteer_type_profile_profile_id"),
        "volunteer_type_profile",
        ["profile_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_volunteer_type_profile_volunteer_type_id"),
        "volunteer_type_profile",
        ["volunteer_type_id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Откат базы данных на чистую."""
    op.drop_index(
        op.f("ix_volunteer_type_profile_volunteer_type_id"),
        table_name="volunteer_type_profile",
    )
    op.drop_index(
        op.f("ix_volunteer_type_profile_profile_id"),
        table_name="volunteer_type_profile",
    )
    op.drop_index(
        op.f("ix_volunteer_type_profile_id"),
        table_name="volunteer_type_profile",
    )
    op.drop_table("volunteer_type_profile")
    op.drop_index(
        op.f("ix_volunteer_type_event_volunteer_type_id"),
        table_name="volunteer_type_event",
    )
    op.drop_index(op.f("ix_volunteer_type_event_id"), table_name="volunteer_type_event")
    op.drop_index(
        op.f("ix_volunteer_type_event_event_id"),
        table_name="volunteer_type_event",
    )
    op.drop_table("volunteer_type_event")
    op.drop_index(op.f("ix_mailing_start_execute_datetime"), table_name="mailing")
    op.drop_index(op.f("ix_mailing_is_executed"), table_name="mailing")
    op.drop_index(op.f("ix_mailing_id"), table_name="mailing")
    op.drop_index(op.f("ix_mailing_event_id"), table_name="mailing")
    op.drop_index(op.f("ix_mailing_end_execute_datetime"), table_name="mailing")
    op.drop_table("mailing")
    op.drop_index(op.f("ix_activity_profile_profile_id"), table_name="activity_profile")
    op.drop_index(op.f("ix_activity_profile_id"), table_name="activity_profile")
    op.drop_index(
        op.f("ix_activity_profile_activity_id"),
        table_name="activity_profile",
    )
    op.drop_table("activity_profile")
    op.drop_index(op.f("ix_activity_event_id"), table_name="activity_event")
    op.drop_index(op.f("ix_activity_event_event_id"), table_name="activity_event")
    op.drop_index(op.f("ix_activity_event_activity_id"), table_name="activity_event")
    op.drop_table("activity_event")
    op.drop_index(op.f("ix_profile_user_id"), table_name="profile")
    op.drop_index(op.f("ix_profile_region_id"), table_name="profile")
    op.drop_index(op.f("ix_profile_is_event_organizer"), table_name="profile")
    op.drop_index(op.f("ix_profile_id"), table_name="profile")
    op.drop_index(op.f("ix_profile_district_id"), table_name="profile")
    op.drop_table("profile")
    op.drop_index(op.f("ix_event_type"), table_name="event")
    op.drop_index(op.f("ix_event_organization_id"), table_name="event")
    op.drop_index(op.f("ix_event_name"), table_name="event")
    op.drop_index(op.f("ix_event_id"), table_name="event")
    op.drop_index(op.f("ix_event_district_id"), table_name="event")
    op.drop_table("event")
    op.drop_index(
        op.f("ix_district_organization_organization_id"),
        table_name="district_organization",
    )
    op.drop_index(
        op.f("ix_district_organization_id"),
        table_name="district_organization",
    )
    op.drop_index(
        op.f("ix_district_organization_district_id"),
        table_name="district_organization",
    )
    op.drop_table("district_organization")
    op.drop_index(
        op.f("ix_activity_organization_organization_id"),
        table_name="activity_organization",
    )
    op.drop_index(
        op.f("ix_activity_organization_id"),
        table_name="activity_organization",
    )
    op.drop_index(
        op.f("ix_activity_organization_activity_id"),
        table_name="activity_organization",
    )
    op.drop_table("activity_organization")
    op.drop_index(op.f("ix_organization_name"), table_name="organization")
    op.drop_index(op.f("ix_organization_id"), table_name="organization")
    op.drop_index(op.f("ix_organization_creator_id"), table_name="organization")
    op.drop_table("organization")
    op.drop_index(op.f("ix_district_type"), table_name="district")
    op.drop_index(op.f("ix_district_region_id"), table_name="district")
    op.drop_index(op.f("ix_district_parent_id"), table_name="district")
    op.drop_index(op.f("ix_district_name"), table_name="district")
    op.drop_index(op.f("ix_district_id"), table_name="district")
    op.drop_table("district")
    op.drop_index(op.f("ix_volunteer_type_name"), table_name="volunteer_type")
    op.drop_index(op.f("ix_volunteer_type_id"), table_name="volunteer_type")
    op.drop_table("volunteer_type")
    op.drop_index(op.f("ix_user_telegram_id"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix_region_name"), table_name="region")
    op.drop_index(op.f("ix_region_id"), table_name="region")
    op.drop_table("region")
    op.drop_index(op.f("ix_employee_id"), table_name="employee")
    op.drop_table("employee")
    op.drop_index(op.f("ix_activity_name"), table_name="activity")
    op.drop_index(op.f("ix_activity_id"), table_name="activity")
    op.drop_table("activity")
    # ### end Alembic commands ###
