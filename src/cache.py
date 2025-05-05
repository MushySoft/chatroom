import datetime
import json
from typing import Any, Optional

from redis.asyncio import Redis

from src.config import settings
from src.constants import (
    TEMP_FILE_KEY,
    TEMP_INVITES_KEY,
    TEMP_PARTICIPANTS_KEY,
    TEMP_ROOMS_KEY,
)

redis_client: Redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def add_file_to_temp_redis(redis: Redis, user_id: int, file_url: str) -> None:
    key = TEMP_FILE_KEY.format(user_id=user_id)
    current_data = await redis.get(key)
    files = json.loads(current_data) if current_data else []

    files.append({"url": file_url, "uploaded_at": datetime.datetime.now().isoformat()})

    await redis.set(key, json.dumps(files), ex=3600)


async def get_temp_files(redis: Redis, user_id: int) -> list[dict[str, Any]]:
    key = TEMP_FILE_KEY.format(user_id=user_id)
    data = await redis.get(key)
    return json.loads(data) if data else []


async def clear_temp_files(redis: Redis, user_id: int) -> None:
    key = TEMP_FILE_KEY.format(user_id=user_id)
    await redis.delete(key)


def serialize_datetime(obj: Any) -> str:
    if hasattr(obj, "isoformat"):
        return str(obj.isoformat())
    return str(obj)


async def get_cached_rooms(
    redis: Redis, user_id: int, limit: int, offset: int
) -> Optional[list[dict[str, Any]]]:
    key = TEMP_ROOMS_KEY.format(user_id=user_id, limit=limit, offset=offset)
    data = await redis.get(key)
    return json.loads(data) if data else None


async def set_cached_rooms(
    redis: Redis, user_id: int, limit: int, offset: int, data: list[dict[str, Any]]
) -> None:
    key = TEMP_ROOMS_KEY.format(user_id=user_id, limit=limit, offset=offset)
    await redis.setex(
        key,
        datetime.timedelta(seconds=15),
        json.dumps(data, default=serialize_datetime),
    )


async def get_cached_participants(
    redis: Redis, room_id: int
) -> Optional[list[dict[str, Any]]]:
    key = TEMP_PARTICIPANTS_KEY.format(room_id=room_id)
    data = await redis.get(key)
    return json.loads(data) if data else None


async def set_cached_participants(
    redis: Redis, room_id: int, data: list[dict[str, Any]]
) -> None:
    key = TEMP_PARTICIPANTS_KEY.format(room_id=room_id)
    await redis.setex(
        key,
        datetime.timedelta(seconds=30),
        json.dumps(data, default=serialize_datetime),
    )


async def delete_cached_participants(redis: Redis, room_id: int) -> None:
    await redis.delete(TEMP_PARTICIPANTS_KEY.format(room_id=room_id))


async def get_cached_invites(
    redis: Redis, user_id: int, sent: bool, limit: int, offset: int
) -> Optional[list[dict[str, Any]]]:
    prefix = "sent" if sent else "received"
    key = TEMP_INVITES_KEY.format(
        user_id=user_id, prefix=prefix, limit=limit, offset=offset
    )
    data = await redis.get(key)
    return json.loads(data) if data else None


async def set_cached_invites(
    redis: Redis,
    user_id: int,
    sent: bool,
    limit: int,
    offset: int,
    data: list[dict[str, Any]],
) -> None:
    prefix = "sent" if sent else "received"
    key = TEMP_INVITES_KEY.format(
        user_id=user_id, prefix=prefix, limit=limit, offset=offset
    )
    await redis.setex(
        key,
        datetime.timedelta(seconds=30),
        json.dumps(data, default=serialize_datetime),
    )
