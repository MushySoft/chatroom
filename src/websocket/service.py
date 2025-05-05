import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core import UserStatus


async def set_user_active(user_id: int, db: AsyncSession):
    status = (
        await db.execute(select(UserStatus).where(UserStatus.user_id == user_id))
    ).scalar_one_or_none()

    if status:
        status.status = "active"
    else:
        db.add(UserStatus(user_id=user_id, status="active"))

    await db.commit()


async def set_user_offline(user_id: int, db: AsyncSession):
    status = (
        await db.execute(select(UserStatus).where(UserStatus.user_id == user_id))
    ).scalar_one_or_none()

    if status:
        status.status = "offline"
        status.last_seen = datetime.datetime.now()
        await db.commit()
