from sqlalchemy import Column, Integer, TIMESTAMP, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from src import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

    room = relationship("Room", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    statuses = relationship("MessageStatus", back_populates="message", cascade="all, delete-orphan")
    files = relationship("FileStorage", back_populates="message", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "room_id": self.room_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "files": [file.file_url for file in self.files] if self.files else []
        }


class MessageStatus(Base):
    __tablename__ = "message_status"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("sent", "delivered", "viewed", "failed", "deleted", name="message_status_enum"), nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.datetime.now, nullable=False)

    message = relationship("Message", back_populates="statuses")
    user = relationship("User", back_populates="message_statuses")
