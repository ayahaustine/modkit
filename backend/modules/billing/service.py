from sqlalchemy.ext.asyncio import AsyncSession


class BillingService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
