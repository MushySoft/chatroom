from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core import User
from src.user.schemas import UsernameUpdate, UserPublic


async def get_user_info(current_user: User) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
    )


async def update_username(
    data: UsernameUpdate, db: AsyncSession, current_user: User
) -> dict[str, str]:
    result = await db.execute(select(User).where(User.username == data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=409, detail="Username is already taken")

    current_user.username = data.username
    await db.commit()
    return {"new_username": data.username}


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


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

    return [
        UserPublic(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar_url=user.avatar_url,
            status=user.status.status if user.status else None,
        )
        for user in users
    ]
