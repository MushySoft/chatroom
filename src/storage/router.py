from fastapi import APIRouter, Depends, File, Response, UploadFile
from redis.asyncio import Redis

from src import get_redis, settings
from src.auth import get_current_user
from src.core import User
from src.storage import service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", summary="Upload file to MINIO")
async def upload_file(  # type: ignore[no-untyped-def]
    response: Response,
    room_id: int,
    result: tuple[User, str | None] = Depends(get_current_user),
    file: UploadFile = File(...),
    redis: Redis = Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.upload_file(
        file=file, redis=redis, current_user=user, room_id=room_id
    )
