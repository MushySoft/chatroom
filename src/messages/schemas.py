from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    room_id: int
    content: str


class MessageUpdate(BaseModel):
    message_id: int
    new_content: Optional[str] = None
    file_urls: List[str] = Field(default_factory=list)


class MessageDTO(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    files: List[str] = Field(default_factory=list)
