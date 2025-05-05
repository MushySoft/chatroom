from pydantic import BaseModel, constr


class UsernameUpdate(BaseModel):
    username: constr(min_length=3, max_length=16)
