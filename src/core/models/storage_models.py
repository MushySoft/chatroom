import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey
)
from sqlalchemy.orm import relationship

from src import Base


class FileStorage(Base):
    __tablename__ = "file_storage"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False
    )
    file_url = Column(
        String(255),
        nullable=False
    )
    created_at = Column(
        TIMESTAMP,
        default=datetime.datetime.now,
        nullable=False
    )

    message = relationship(
        "Message",
        back_populates="files"
    )

