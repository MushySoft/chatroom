from typing import Annotated, Optional

from pydantic import BaseModel, Field


class UsernameUpdateRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]


class UsernameUpdateResponse(BaseModel):
    new_username: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}
