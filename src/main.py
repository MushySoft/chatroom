from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mushysoft.online",   # разрешаем фронту
        "http://localhost:3000"       # для разработки
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def ping():
    return {"message": "pong"}

from src.auth import router as auth_router
from src.storage import router as storage_router
from src.messages import router as messages_router
from src.messages import ws_router as messages_ws_router
from src.messages import ws_docs_router as messages_ws_docs_router
from src.rooms import router as rooms_router
from src.websocket import ws_router, ws_docs_router
app.include_router(auth_router)
app.include_router(storage_router)
app.include_router(messages_router)
app.include_router(rooms_router)
app.include_router(ws_router)
app.include_router(ws_docs_router)
app.include_router(messages_ws_router)
app.include_router(messages_ws_docs_router)