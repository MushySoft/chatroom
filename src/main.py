from fastapi import FastAPI
from src.config import settings

app = FastAPI(
    title="Chatroom API",
    description="API для многокомнатного чата",
    version="0.0.1",
    debug=settings.DEBUG
)


@app.get("/")
async def ping():
    return {"message": "pong"}
