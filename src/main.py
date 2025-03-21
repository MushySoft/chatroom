from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from src.config import settings

app = FastAPI(
    title="Chatroom API",
    description="API для многокомнатного чата",
    version="0.0.1",
    debug=settings.DEBUG
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.get("/")
async def ping():
    return {"message": "pong"}

from src.auth import router as auth_router
app.include_router(auth_router)
