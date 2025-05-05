import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship

from src import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    auth_provider = Column(String(255))
    auth_id = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )
    avatar_url = Column(String(512), nullable=True)
    refresh_token = Column(String(1024), nullable=True)

    status = relationship(
        "UserStatus", back_populates="user", uselist=False, cascade="all, delete-orphan"
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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status = Column(
        Enum("active", "offline", "do_not_disturb", name="user_status_enum"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )

    user = relationship("User", back_populates="status")

    __table_args__ = (Index("ix_user_status_user_id", "user_id"),)
