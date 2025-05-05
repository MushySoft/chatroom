import json
import datetime

from redis import asyncio
from redis.asyncio import Redis

from src.config import settings
from src.constants import (
    TEMP_FILE_KEY,
    TEMP_ROOMS_KEY,
    TEMP_PARTICIPANTS_KEY,
    TEMP_INVITES_KEY
)

redis_client = asyncio.from_url(settings.REDIS_URL, decode_responses=True)


async def add_file_to_temp_redis(redis: Redis, user_id: int, file_url: str):
    key = TEMP_FILE_KEY.format(user_id=user_id)
    current_data = await redis.get(key)
    files = json.loads(current_data) if current_data else []

    files.append({
        "url": file_url,
        "uploaded_at": datetime.datetime.now().isoformat()
    })

    await redis.set(key, json.dumps(files), ex=3600)


async def get_temp_files(redis: Redis, user_id: int) -> list:
    key = TEMP_FILE_KEY.format(user_id=user_id)
    data = await redis.get(key)
    return json.loads(data) if data else []


async def clear_temp_files(redis: Redis, user_id: int):
    key = TEMP_FILE_KEY.format(user_id=user_id)
    await redis.delete(key)


def serialize_datetime(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


async def get_cached_rooms(redis: Redis, user_id: int, limit: int, offset: int):
    key = TEMP_ROOMS_KEY.format(user_id=user_id, limit=limit, offset=offset)
    data = await redis.get(key)
    if data:
        return json.loads(data)


async def set_cached_rooms(redis: Redis, user_id: int, limit: int, offset: int, data: list):
    key = TEMP_ROOMS_KEY.format(user_id=user_id, limit=limit, offset=offset)
    await redis.setex(
        key,
        datetime.timedelta(seconds=15),
        json.dumps(data, default=serialize_datetime)
    )


async def get_cached_participants(redis: Redis, room_id: int):
    key = TEMP_PARTICIPANTS_KEY.format(room_id=room_id)
    data = await redis.get(key)
    if data:
        return json.loads(data)


async def set_cached_participants(redis: Redis, room_id: int, data: list):
    key = TEMP_PARTICIPANTS_KEY.format(room_id=room_id)
    await redis.setex(
        key,
        datetime.timedelta(seconds=30),
        json.dumps(data, default=serialize_datetime)
    )


async def delete_cached_participants(redis: Redis, room_id: int):
    await redis.delete(TEMP_PARTICIPANTS_KEY.format(room_id=room_id))


async def get_cached_invites(redis: Redis, user_id: int, sent: bool, limit: int, offset: int):
    prefix = "sent" if sent else "received"
    key = TEMP_INVITES_KEY.format(user_id=user_id, prefix=prefix, limit=limit, offset=offset)
    data = await redis.get(key)
    if data:
        return json.loads(data)


async def set_cached_invites(redis: Redis, user_id: int, sent: bool, limit: int, offset: int, data: list):
    prefix = "sent" if sent else "received"
    key = TEMP_INVITES_KEY.format(user_id=user_id, prefix=prefix, limit=limit, offset=offset)
    await redis.setex(
        key,
        datetime.timedelta(seconds=30),
        json.dumps(data, default=serialize_datetime)
    )


# async def delete_all_invite_caches(redis: Redis, user_id: int):
#     # Можно сделать через SCAN и DEL по шаблону user:{user_id}:*invites*
#     # или просто удалить конкретные ключи, если нужно сразу
#     pass  # опционально
