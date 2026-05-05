from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from core.config import settings
from core.database import get_db
from core.dependencies import CurrentUser
from modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from modules.auth.service import AuthService
from modules.users.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_OPTS = dict(
    httponly=True,
    secure=settings.COOKIE_SECURE,
    samesite=settings.COOKIE_SAMESITE,
    domain=settings.COOKIE_DOMAIN,
)


def _set_tokens(response: Response, access_token: str, refresh_token: str) -> None:
    """Write access_token and refresh_token as httpOnly cookies on the response."""
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        **_COOKIE_OPTS,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth",  # scoped so browsers only send it to refresh/logout
        **_COOKIE_OPTS,
    )


def _clear_tokens(response: Response) -> None:
    """Remove auth cookies from the response on logout."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/auth")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> UserOut:
    return await AuthService(db, request).register(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> TokenResponse:
    _, access_token, refresh_token = await AuthService(db, request).login(data)
    _set_tokens(response, access_token, refresh_token)
    return TokenResponse()


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    old_refresh = request.cookies.get("refresh_token")
    new_access, new_refresh = await AuthService(db, request).refresh(old_refresh or "")
    _set_tokens(response, new_access, new_refresh)
    return TokenResponse()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    refresh_token = request.cookies.get("refresh_token", "")
    await AuthService(db, request).logout(refresh_token)
    _clear_tokens(response)


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)
