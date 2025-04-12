from pydantic import BaseModel
from datetime import datetime


class RoomCreate(BaseModel):
    name: str
    is_private: bool


class RoomInvite(BaseModel):
    room_id: int
    receiver_id: int


class RoomInviteRespond(BaseModel):
    invitation_id: int
    accept: bool


class RoomInvitationOut(BaseModel):
    id: int
    room_id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class RoomParticipantOut(BaseModel):
    user_id: int
    joined_at: datetime

    class Config:
        orm_mode = True


class RoomOut(BaseModel):
    id: int
    name: str
    is_private: bool
    created_by: int
    created_at: datetime

    class Config:
        orm_mode = True


class LastMessageOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    sender_id: int

    class Config:
        orm_mode = True


class RoomWithLastMessageOut(BaseModel):
    id: int
    name: str
    is_private: bool
    created_by: int
    created_at: datetime
    last_message: LastMessageOut | None


class RoomUpdate(BaseModel):
    name: str | None = None
    is_private: bool | None = None
