import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Enum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import Base

if TYPE_CHECKING:
    from src.core.models.message_models import Message
    from src.core.models.user_models import User


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )

    creator: Mapped["User"] = relationship(back_populates="created_rooms")
    participants: Mapped[list["RoomUser"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(back_populates="room")
    invitations: Mapped[list["RoomInvitation"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class RoomUser(Base):
    __tablename__ = "room_user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    joined_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )

    room: Mapped["Room"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="room_memberships")

    __table_args__ = (
        Index("ix_room_user_user_id", "user_id"),
        Index("ix_room_user_room_id", "room_id"),
    )


class RoomInvitation(Base):
    __tablename__ = "room_invitations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )

    room: Mapped["Room"] = relationship(back_populates="invitations")
    sender: Mapped["User"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id])
    status: Mapped["RoomInvitationStatus"] = relationship(
        back_populates="invitation",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_room_invitations_sender_id", "sender_id"),
        Index("ix_room_invitations_receiver_id", "receiver_id"),
    )


class RoomInvitationStatus(Base):
    __tablename__ = "room_invitation_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invitation_id: Mapped[int] = mapped_column(
        ForeignKey("room_invitations.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "rejected", name="invitation_status_enum"),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now, nullable=False
    )

    invitation: Mapped["RoomInvitation"] = relationship(back_populates="status")
