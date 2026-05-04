from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from modules.auth.router import router as auth_router
from modules.billing.router import router as billing_router
from modules.users.router import router as users_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(billing_router, prefix=API_PREFIX)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}
