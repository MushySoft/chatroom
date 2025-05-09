from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core import User
from src.user.schemas import UsernameUpdateRequest, UsernameUpdateResponse, UserPublic


async def get_user_info(current_user: User) -> UserPublic:
    return UserPublic.model_validate(current_user)


async def update_username(
    data: UsernameUpdateRequest, db: AsyncSession, current_user: User
) -> UsernameUpdateResponse:
    result = await db.execute(select(User).where(User.username == data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=409, detail="Username is already taken")

    current_user.username = data.username
    await db.commit()
    return UsernameUpdateResponse(new_username=data.username)


async def get_user_by_id(user_id: int, db: AsyncSession) -> UserPublic:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user)


async def search_users(
    username: Optional[str], email: Optional[str], db: AsyncSession
) -> list[UserPublic]:
    query = select(User).options(joinedload(User.status))

    if username:
        query = query.where(User.username.ilike(f"%{username}%"))
    if email:
        query = query.where(User.email.ilike(f"%{email}%"))

    result = await db.execute(query)
    users = result.scalars().all()

    return [UserPublic.model_validate(user) for user in users]
