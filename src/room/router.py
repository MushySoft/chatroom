from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.deps import get_current_user
from src.deps import get_db
from src.core.models import User
from src.room import service
from src.room.schemas import (
    RoomCreate, RoomInvite, RoomInviteRespond
)

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", summary="Create a room")
async def create_room(
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.create_room(data=data, db=db, current_user=current_user)


@router.post("/invite", summary="Invite user to a room")
async def invite_user(
    data: RoomInvite,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await service.invite_user(data=data, db=db, current_user=current_user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/invitations/sent", summary="View sent invitations")
async def sent_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_sent_invites(db=db, current_user=current_user)


@router.get("/invitations/received", summary="View received invitations")
async def received_invitations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_received_invites(db=db, current_user=current_user)


@router.post("/invitations/respond", summary="Respond to invitation")
async def respond_to_invite(
    data: RoomInviteRespond,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await service.respond_to_invite(data=data, db=db, current_user=current_user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{room_id}/users/{user_id}", summary="Remove user from room")
async def remove_user(
    room_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await service.remove_user_from_room(room_id=room_id, user_id=user_id, db=db, current_user=current_user)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{room_id}/leave", summary="Leave room")
async def leave_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.leave_room(room_id=room_id, db=db, current_user=current_user)


@router.get("/{room_id}/participants", summary="List room participants")
async def get_participants(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_room_participants(room_id=room_id, db=db)
