import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.models import Session


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        refresh_token: str,
        expire_days: int,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            token_hash=_hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=expire_days),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_by_token(self, refresh_token: str) -> Session | None:
        token_hash = _hash_token(refresh_token)
        result = await self.db.execute(
            select(Session).where(
                Session.token_hash == token_hash,
                Session.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def rotate(
        self,
        old_session: Session,
        new_refresh_token: str,
        expire_days: int,
    ) -> Session:
        """Replace the token hash in-place (token rotation)."""
        old_session.token_hash = _hash_token(new_refresh_token)
        old_session.expires_at = datetime.now(timezone.utc) + timedelta(days=expire_days)
        await self.db.flush()
        return old_session

    async def delete(self, session: Session) -> None:
        await self.db.delete(session)
        await self.db.flush()

    async def delete_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.db.execute(delete(Session).where(Session.user_id == user_id))
        await self.db.flush()
