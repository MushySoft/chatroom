from fastapi import UploadFile
from redis.asyncio import Redis

from src import add_file_to_temp_redis, upload_file_to_minio
from src.core import User


async def upload_file(
    room_id: int, file: UploadFile, redis: Redis, current_user: User
) -> dict[str, str]:
    content = await file.read()
    file_url = upload_file_to_minio(
        content,
        file.filename if file.filename else "None",
        file.content_type if file.content_type else "None",
    )
    await add_file_to_temp_redis(redis, current_user.id, file_url, room_id)
    return {"file_url": file_url}
