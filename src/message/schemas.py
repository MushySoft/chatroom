from pydantic import BaseModel
from typing import Optional, List


class MessageCreate(BaseModel):
    room_id: int
    content: Optional[str] = None
    file_urls: List[str] = []
