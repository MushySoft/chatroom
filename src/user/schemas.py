from typing import Annotated, Optional

from pydantic import BaseModel, Field


class UsernameUpdate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=16)]


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    status: Optional[str] = None
