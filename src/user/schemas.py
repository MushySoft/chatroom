from pydantic import BaseModel, constr
from typing import Optional


class UsernameUpdate(BaseModel):
    username: constr(min_length=3, max_length=16)


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    status: Optional[str] = None
