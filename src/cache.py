from redis import asyncio
from redis.asyncio import Redis
import json
from datetime import datetime

from src.config import settings
from src.constants import TEMP_FILE_KEY

redis_client = asyncio.from_url(settings.REDIS_URL, decode_responses=True)


async def add_file_to_temp_redis(redis: Redis, user_id: int, file_url: str):
    key = TEMP_FILE_KEY.format(user_id=user_id)
    current_data = await redis.get(key)
    files = json.loads(current_data) if current_data else []

    files.append({
        "url": file_url,
        "uploaded_at": datetime.now().isoformat()
    })

    await redis.set(key, json.dumps(files), ex=3600)  # 1 час хранения


async def get_temp_files(redis: Redis, user_id: int) -> list:
    key = TEMP_FILE_KEY.format(user_id=user_id)
    data = await redis.get(key)
    return json.loads(data) if data else []


async def clear_temp_files(redis: Redis, user_id: int):
    key = TEMP_FILE_KEY.format(user_id=user_id)
    await redis.delete(key)
