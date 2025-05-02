from fastapi import APIRouter, UploadFile, File, Depends, Response
from src.auth.deps import get_current_user
from src import get_redis, settings
from src.storage import service
from src.core.models import User

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", summary="Upload file to MINIO")
async def upload_file(
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        file: UploadFile = File(...),
        redis=Depends(get_redis),
):
    user, new_token = result
    if new_token:
        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.TOKEN_EXPIRE_SECONDS
        )
    return await service.upload_file(
        file=file,
        redis=redis,
        current_user=user
    )
