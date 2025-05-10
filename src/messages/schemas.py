from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    room_id: int
    content: str


class MessageCreateResponse(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageUpdateRequest(BaseModel):
    message_id: int
    new_content: Optional[str] = None
    file_urls: List[str] = Field(default_factory=list)


class MessageUpdateResponse(BaseModel):
    message_id: int
    status: str = "updated"

    model_config = {"from_attributes": True}


class MessageDeleteResponse(BaseModel):
    message_id: int
    status: str = "deleted"

    model_config = {"from_attributes": True}


class MessageSender(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class MessagePublic(BaseModel):
    id: int
    room_id: int
    sender_id: int
    sender: MessageSender
    content: str
    created_at: datetime
    updated_at: datetime
    files: List[str] = Field(default_factory=list)
    status: str | None
    is_owner: bool

    model_config = {"from_attributes": True}
