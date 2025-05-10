from datetime import datetime

from pydantic import BaseModel


class RoomCreateRequest(BaseModel):
    name: str
    is_private: bool


class RoomCreateResponse(BaseModel):
    id: int
    name: str
    is_private: bool
    created_by: int
    created_at: datetime
    updated_at: datetime


class RoomInviteRequest(BaseModel):
    room_id: int
    receiver_id: int


class RoomInviteResponse(BaseModel):
    invitation_id: int
    status: str = "pending"


class RoomInviteRespondRequest(BaseModel):
    invitation_id: int
    accept: bool


class RoomInviteRespondResponse(BaseModel):
    status: str


class RoomInvitationOut(BaseModel):
    id: int
    room_id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoomParticipantOut(BaseModel):
    user_id: int
    joined_at: datetime

    model_config = {"from_attributes": True}


class LastMessageOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    sender_id: int

    model_config = {"from_attributes": True}


class RoomWithLastMessageOut(BaseModel):
    id: int
    name: str
    is_private: bool
    created_by: int
    created_at: datetime
    last_message: LastMessageOut | None

    model_config = {"from_attributes": True}


class RoomUpdateRequest(BaseModel):
    name: str | None = None
    is_private: bool | None = None


class RoomUpdateResponse(BaseModel):
    status: str = "updated"


class RemoveUserResponse(BaseModel):
    status: str = "removed"


class LeaveRoomResponse(BaseModel):
    status: str = "left"


class RoomSearchResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class RoomJoinResponse(BaseModel):
    id: int
    name: str
    is_private: bool
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}
