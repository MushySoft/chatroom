from redis import asyncio
from src.config import settings

redis_client = asyncio.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    return redis_client
