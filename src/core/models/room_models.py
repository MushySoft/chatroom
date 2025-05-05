import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship

from src import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    is_private = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    creator = relationship("User", back_populates="created_rooms")
    participants = relationship(
        "RoomUser", back_populates="room", cascade="all, delete-orphan"
    )
    messages = relationship("Message", back_populates="room")
    invitations = relationship(
        "RoomInvitation", back_populates="room", cascade="all, delete-orphan"
    )


class RoomUser(Base):
    __tablename__ = "room_user"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    joined_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

    room = relationship("Room", back_populates="participants")
    user = relationship("User", back_populates="room_memberships")

    __table_args__ = (
        Index("ix_room_user_user_id", "user_id"),
        Index("ix_room_user_room_id", "room_id"),
    )


class RoomInvitation(Base):
    __tablename__ = "room_invitations"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    sender_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    receiver_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

    room = relationship("Room", back_populates="invitations")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    status = relationship(
        "RoomInvitationStatus",
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

    id = Column(Integer, primary_key=True, index=True)
    invitation_id = Column(
        Integer, ForeignKey("room_invitations.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(
        Enum("pending", "accepted", "rejected", name="invitation_status_enum"),
        nullable=False,
    )
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

    invitation = relationship("RoomInvitation", back_populates="status")
