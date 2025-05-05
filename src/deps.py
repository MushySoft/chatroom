from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import AsyncGenerator

from src.cache import redis_client
from src.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> Redis:
    return redis_client
