from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from modules.auth.repository import SessionRepository
from modules.auth.schemas import LoginRequest, RegisterRequest
from modules.users.models import User
from modules.users.repository import UserRepository
from modules.users.schemas import UserOut


class AuthService:
    def __init__(self, db: AsyncSession, request: Request) -> None:
        self.db = db
        self.request = request
        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)

    def _client_meta(self) -> tuple[str | None, str | None]:
        user_agent = self.request.headers.get("user-agent")
        ip = self.request.client.host if self.request.client else None
        return user_agent, ip

    async def register(self, data: RegisterRequest) -> UserOut:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = await self.users.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )
        return UserOut.model_validate(user)

    async def login(self, data: LoginRequest) -> tuple[User, str, str]:
        user = await self.users.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        user_agent, ip = self._client_meta()
        await self.sessions.create(
            user_id=user.id,
            refresh_token=refresh_token,
            expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            user_agent=user_agent,
            ip_address=ip,
        )
        return user, access_token, refresh_token

    async def refresh(self, old_refresh_token: str) -> tuple[str, str]:
        """Validate existing session, rotate tokens, return new pair."""
        session = await self.sessions.get_by_token(old_refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
            )

        new_access = create_access_token(str(session.user_id))
        new_refresh = create_refresh_token(str(session.user_id))

        await self.sessions.rotate(
            session, new_refresh, expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        return new_access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        session = await self.sessions.get_by_token(refresh_token)
        if session:
            await self.sessions.delete(session)
