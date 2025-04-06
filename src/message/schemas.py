from pydantic import BaseModel
from typing import Optional, List


class MessageCreate(BaseModel):
    room_id: int
    content: Optional[str] = None
    file_urls: List[str] = []


class MessageUpdate(BaseModel):
    message_id: int
    new_content: Optional[str] = None
    file_urls: List[str] = []
