from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.repository import UserRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)
