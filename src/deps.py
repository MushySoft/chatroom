from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import AsyncGenerator

from src.database import AsyncSessionLocal
from src.cache import redis_client

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis():
    return redis_client
