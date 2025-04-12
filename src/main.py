from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware
from src.config import settings

app = FastAPI(
    debug=settings.DEBUG
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Chatroom API",
        version="0.0.1",
        description="API для многокомнатного чата",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
async def ping():
    return {"message": "pong"}

from src.auth import router as auth_router
from src.storage import router as storage_router
from src.message import router as message_router
from src.room import router as room_router
from src.chat import router as chat_router
app.include_router(auth_router)
app.include_router(storage_router)
app.include_router(message_router)
app.include_router(room_router)
app.include_router(chat_router)