from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src import Pagination, settings
from src.auth.deps import get_current_user
from src.messages.schemas import MessageCreate, MessageUpdate
from src.deps import get_db, get_redis
from src.core.models import User
from src.messages import service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", summary="Send a messages")
async def send_message(
        data: MessageCreate,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
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
    return await service.send_message(
        data=data,
        db=db,
        redis=redis,
        current_user=user
    )


@router.get("/room/{room_id}", summary="Get messages from a rooms")
async def get_messages_by_room(
        room_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        pagination: Pagination = Depends(Pagination),
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
    return await service.get_messages_by_room(
        room_id=room_id,
        db=db,
        current_user=user,
        pagination=pagination,
    )


@router.get("/{message_id}", summary="Get a messages by ID")
async def get_message_by_id(
        message_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
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
    message = await service.get_message_by_id(
        message_id=message_id,
        db=db,
        current_user=user
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found or access denied")
    return message


@router.put("/", summary="Update a messages")
async def update_message(
        data: MessageUpdate,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
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
    try:
        return await service.update_message(
            data=data,
            db=db,
            current_user=user
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Message not found")
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")


@router.delete("/{message_id}", summary="Delete a messages (soft delete)")
async def delete_message(
        message_id: int,
        response: Response,
        result: tuple[User, str | None] = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
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
    return await service.delete_message(
        message_id=message_id,
        db=db,
        current_user=user
    )
