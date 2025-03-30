from fastapi import APIRouter, UploadFile, File, Depends
from src.auth.deps import get_current_user
from src import get_redis
from src.storage import service
from src.core.models import User

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        redis=Depends(get_redis),
        current_user: User = Depends(get_current_user)
):
    return await service.upload_file(file=file, redis=redis, current_user=current_user)
