from fastapi import HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.user.models import User, UserStatus
from src.config import settings
import os

oauth = OAuth()
oauth.register(
    "google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    userinfo_endpoint="https://www.googleapis.com/oauth2/v3/userinfo",
    client_kwargs={"scope": "openid email profile"},
)

async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def auth_callback(request: Request, db: AsyncSession):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Ошибка авторизации")

    user = await db.execute(
        User.select().where(User.email == user_info["email"])
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
        UserStatus.select().where(UserStatus.user_id == user.id)
    )
    status = status.scalar_one_or_none()

    if not status:
        status = UserStatus(user_id=user.id, status="active")
        db.add(status)
    else:
        status.status = "active"

    await db.commit()

    return {"access_token": token["access_token"], "token_type": "bearer"}