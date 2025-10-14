from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class AuthenticationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, username: str, password: str) -> User:
        user = User(username=username, password=password)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user