from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import get_current_user
from src.message.schemas import MessageCreate
from src.deps import get_db, get_redis
from src.core.models import User

from src.message import service

router = APIRouter(prefix="/message", tags=["message"])


@router.post("/send")
async def send_message(
        data: MessageCreate,
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis),
        current_user: User = Depends(get_current_user)
):

    return await service.send_message(data=data, db=db, redis=redis, current_user=current_user)
