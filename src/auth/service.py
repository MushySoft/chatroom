from fastapi import HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.models import User, UserStatus
from src.config import settings
import logging

logger = logging.getLogger(__name__)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def login(request: Request):
    redirect_uri = str(request.url_for("auth_callback")).replace("http://", "https://")
    response = await oauth.google.authorize_redirect(request, redirect_uri)
    return response


async def auth_callback(request: Request, db: AsyncSession):
    token = await oauth.google.authorize_access_token(request)
    logger.info(token)
    user_info = await oauth.google.userinfo(token=token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Ошибка авторизации")

    user = await db.execute(
        select(User).where(User.email == user_info["email"])
    )
    user = user.scalar_one_or_none()

    if not user:
        user = User(
            username=user_info["name"],
            email=user_info["email"],
            auth_provider="google",
            auth_id=user_info["sub"]
        )
        db.add(user)
        await db.commit()

    status = await db.execute(
        select(UserStatus).where(UserStatus.user_id == user.id)
    )
    status = status.scalar_one_or_none()

    if not status:
        status = UserStatus(user_id=user.id, status="active")
        db.add(status)
    else:
        status.status = "active"

    await db.commit()

    return {"access_token": token["access_token"], "token_type": "bearer"}