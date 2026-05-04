from sqlalchemy.ext.asyncio import AsyncSession


class BillingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
