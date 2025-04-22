from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import AsyncGenerator
from typing import Annotated
from fastapi import Depends

from src.database import AsyncSessionLocal
from src.cache import redis_client
from src.pagination import Pagination

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis():
    return redis_client

PaginationDep = Annotated[Pagination, Depends()]
