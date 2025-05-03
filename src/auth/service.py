from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.auth.schemas import UsernameUpdate
from src.core.models import User, UserStatus
from src.config import settings
from src import upload_file_to_minio
import logging
import aiohttp

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
    if settings.DEBUG:
        redirect_uri = str(request.url_for("auth_callback"))
    else:
        redirect_uri = str(request.url_for("auth_callback")).replace("http://", "https://")
    response = await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        access_type="offline",
        prompt="consent"
    )
    return response


async def auth_callback(
        request: Request,
        db: AsyncSession
):
    token = await oauth.google.authorize_access_token(request)
    logger.info(token)

    access_token = token["access_token"]
    refresh_token = token.get("refresh_token")  # может быть None

    user_info = await oauth.google.userinfo(token=token)

    if not user_info:
        raise HTTPException(status_code=400, detail="Ошибка авторизации")

    avatar_url = user_info.get("picture")

    avatar_minio_url = None
    if avatar_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(avatar_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        filename = f"avatars/{user_info['sub']}.jpg"
                        avatar_minio_url = upload_file_to_minio(content, filename, "image/jpeg")
        except Exception as e:
            logger.warning(f"Ошибка при загрузке аватарки: {e}")

    user = await db.execute(
        select(User).where(User.email == user_info["email"])
    )
    user = user.scalar_one_or_none()

    if not user:
        user = User(
            username=user_info["name"],
            email=user_info["email"],
            auth_provider="google",
            auth_id=user_info["sub"],
            avatar_url=avatar_minio_url,
            refresh_token=refresh_token
        )
        db.add(user)
        await db.commit()
    elif not user.avatar_url and avatar_minio_url:
        user.avatar_url = avatar_minio_url
        if refresh_token:
            user.refresh_token = refresh_token
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

    if settings.DEBUG:
        return JSONResponse({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url
            }
        })

    response = RedirectResponse(settings.REDIRECT_URL)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.TOKEN_EXPIRE_SECONDS,
    )

    return response


async def logout(
        db: AsyncSession,
        current_user: User
):
    user_status = (await db.execute(
        select(UserStatus).where(UserStatus.user_id == current_user.id)
    )).scalar_one_or_none()

    if not user_status:
        status = UserStatus(user_id=current_user.id, status="offline")
        db.add(status)
    else:
        user_status.status = "offline"

    user = (await db.execute(
        select(User).where(User.id == current_user.id)
    )).scalar_one_or_none()

    if user:
        user.refresh = None

    await db.commit()