import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import BaseUserSchema, SelfUserSchema, UserCreateSchema, UserUpdateSchema
from src.config.security import PasswordHasher

log = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def _get_or_404(self, user_id) -> User:
        db_user = await self.repo.get_user(user_id)
        if not db_user:
            log.warning(f'User not found with id: {user_id}')
            raise HTTPException(404, 'User not found')
        return db_user

    async def get_user_by_id(self, user_id) -> BaseUserSchema:
        return BaseUserSchema.model_validate(await self._get_or_404(user_id))

    async def get_self_user(self, user_id) -> SelfUserSchema:
        db_user = await self.repo.get_user_eager(user_id)
        if not db_user:
            log.warning(f'User not found with id: {user_id}')
            raise HTTPException(404, 'User not found')
        return SelfUserSchema.model_validate(db_user)

    async def create_user(self, user_data: UserCreateSchema) -> BaseUserSchema:
        password_hash = PasswordHasher.get_password_hash(user_data.password)
        user = await self.repo.create_user(user_data.username, password_hash)
        log.info(f'User created with name: {user.username}')
        return BaseUserSchema.model_validate(user)

    async def update_user(self, user_id: int, update_fields: UserUpdateSchema) -> BaseUserSchema:
        db_user = await self._get_or_404(user_id)
        db_user = await self.repo.update_user(db_user, **update_fields.model_dump(exclude_unset=True))
        return BaseUserSchema.model_validate(db_user)

    async def deactivate_user(self, user_id: int) -> bool:
        db_user = await self._get_or_404(user_id)
        is_deactivated = await self.repo.deactivate_user(db_user)
        return is_deactivated
