from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)

    model_config = {"from_attributes": True}
