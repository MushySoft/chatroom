from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src import Pagination
from src.auth.deps import get_current_user
from src.messages.schemas import MessageCreate, MessageUpdate
from src.deps import get_db, get_redis
from src.core.models import User
from src.messages import service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", summary="Send a messages")
async def send_message(
        data: MessageCreate,
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
        current_user: User = Depends(get_current_user)
):
    return await service.send_message(
        data=data,
        db=db,
        redis=redis,
        current_user=current_user
    )


@router.get("/room/{room_id}", summary="Get messages from a room")
async def get_messages_by_room(
        room_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        pagination: Pagination = Depends(Pagination),
):
    return await service.get_messages_by_room(
        room_id=room_id,
        db=db,
        current_user=current_user,
        pagination=pagination,
    )


@router.get("/{message_id}", summary="Get a messages by ID")
async def get_message_by_id(
        message_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    message = await service.get_message_by_id(
        message_id=message_id,
        db=db,
        current_user=current_user
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or access denied")
    return message


@router.put("/", summary="Update a messages")
async def update_message(
        data: MessageUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        return await service.update_message(
            data=data,
            db=db,
            current_user=current_user
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Message not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.delete("/{message_id}", summary="Delete a messages (soft delete)")
async def delete_message(
        message_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await service.delete_message(
        message_id=message_id,
        db=db,
        current_user=current_user
    )
