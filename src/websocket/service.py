import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import UserStatus


async def set_user_active(user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(UserStatus).where(UserStatus.user_id == user_id))
    status = result.scalar_one_or_none()

    if status:
        status.status = "active"
    else:
        db.add(UserStatus(user_id=user_id, status="active"))

    await db.commit()


async def set_user_offline(user_id: int, db: AsyncSession) -> None:
    result = await db.execute(select(UserStatus).where(UserStatus.user_id == user_id))
    status = result.scalar_one_or_none()

    if status:
        status.status = "offline"
        status.updated_at = datetime.datetime.now()
        await db.commit()
