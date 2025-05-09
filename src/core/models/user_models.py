import datetime

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(255), nullable=True)
    auth_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(1024), nullable=True)

    status: Mapped["UserStatus"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    created_rooms = relationship("Room", back_populates="creator")
    room_memberships = relationship("RoomUser", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    message_statuses = relationship("MessageStatus", back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_auth_id", "auth_id"),
    )


class UserStatus(Base):
    __tablename__ = "user_status"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "offline", "do_not_disturb", name="user_status_enum"),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="status")

    __table_args__ = (Index("ix_user_status_user_id", "user_id"),)
