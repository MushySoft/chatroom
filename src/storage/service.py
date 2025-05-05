from redis.asyncio import Redis
from fastapi import UploadFile

from src import add_file_to_temp_redis, upload_file_to_minio
from src.core import User


async def upload_file(file: UploadFile, redis: Redis, current_user: User):
    content = await file.read()
    file_url = upload_file_to_minio(content, file.filename, file.content_type)
    await add_file_to_temp_redis(redis, current_user.id, file_url)
    return {"file_url": file_url}
