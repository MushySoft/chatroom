from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from src import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    auth_provider = Column(String(255))
    auth_id = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    status = relationship("UserStatus", back_populates="user", uselist=False, cascade="all, delete-orphan")
    created_rooms = relationship("Room", back_populates="creator")
    room_memberships = relationship("RoomUser", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    message_statuses = relationship("MessageStatus", back_populates="user")


class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    status = Column(Enum("active", "offline", "do_not_disturb", name="status_enum"), nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now, nullable=False)

    user = relationship("User", back_populates="status")
