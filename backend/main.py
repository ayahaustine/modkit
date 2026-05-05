from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from modules.auth.router import router as auth_router
from modules.users.router import router as users_router

API_PREFIX = "/api/v1"

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=f"{API_PREFIX}/docs" if settings.DEBUG else None,
    redoc_url=f"{API_PREFIX}/redoc" if settings.DEBUG else None,
    openapi_url=f"{API_PREFIX}/openapi.json" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)



@app.get(f"{API_PREFIX}/health")
async def health() -> dict:
    """Return service liveness status and current version."""
    return {"status": "ok", "version": settings.APP_VERSION}
