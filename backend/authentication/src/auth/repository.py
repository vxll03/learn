from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.auth.models import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, username: str, password: str) -> User:
        user = User(username=username, password=password)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: int) -> User | None:
        return await self.db.scalar(select(User).where(User.id == user_id))

    async def get_user_eager(self, user_id: int) -> User | None:
        return await self.db.scalar(
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(getattr(User, 'role')),
                selectinload(getattr(User, 'groups')),
            ),
        )
    
    async def get_user_by_username(self, username: str) -> User | None:
        return await self.db.scalar(select(User).where(User.username == username))

    async def deactivate_user(self, user: User) -> bool:
        user.is_active = False
        await self.db.flush()
        return True

    async def update_user(self, user: User, **kwargs) -> User | None:
        for key, value in kwargs.items():
            if value is None:
                continue
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
