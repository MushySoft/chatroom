from typing import List

from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src import Pagination, get_db, get_redis, settings
from src.auth.deps import get_current_user
from src.core import User
from src.messages import service
from src.messages.schemas import (
    MessageCreateRequest,
    MessageCreateResponse,
    MessageDeleteResponse,
    MessagePublic,
    MessageUpdateRequest,
    MessageUpdateResponse,
)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post(
    "/", summary="Send a message", response_model=MessageCreateResponse, status_code=201
)
async def send_message(  # type: ignore[no-untyped-def]
    data: MessageCreateRequest,
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.send_message(data=data, db=db, redis=redis, current_user=user)


@router.get(
    "/room/{room_id}",
    summary="Get messages from a room",
    response_model=List[MessagePublic],
    status_code=200,
)
async def get_messages_by_room(  # type: ignore[no-untyped-def]
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_messages_by_room(
        room_id=room_id,
        db=db,
        current_user=user,
        pagination=pagination,
    )


@router.get(
    "/{message_id}",
    summary="Get a message by ID",
    response_model=MessagePublic,
    status_code=200,
)
async def get_message_by_id(  # type: ignore[no-untyped-def]
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.get_message_by_id(
        message_id=message_id, db=db, current_user=user
    )


@router.patch(
    "/",
    summary="Update a message",
    response_model=MessageUpdateResponse,
    status_code=200,
)
async def update_message(  # type: ignore[no-untyped-def]
    data: MessageUpdateRequest,
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.update_message(data=data, db=db, current_user=user)


@router.delete(
    "/{message_id}",
    summary="Delete a message (soft delete)",
    response_model=MessageDeleteResponse,
    status_code=200,
)
async def delete_message(  # type: ignore[no-untyped-def]
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.delete_message(message_id=message_id, db=db, current_user=user)


@router.get(
    "/search/{text}",
    summary="Search a message",
    response_model=list[MessagePublic],
    status_code=200,
)
async def search_messages(  # type: ignore[no-untyped-def]
    room_id: int,
    text: str,
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
            samesite="none",
            domain=".mushysoft.online",
            max_age=settings.TOKEN_EXPIRE_SECONDS,
        )
    return await service.search_messages(
        room_id=room_id, text=text, db=db, current_user=user
    )
