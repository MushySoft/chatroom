from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
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
app.include_router(auth_router)
