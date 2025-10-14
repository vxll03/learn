import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.repository import AuthenticationRepository
from src.auth.schemas import BaseUserSchema, UserCreateSchema

log = logging.getLogger(__name__)

class AuthenticationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuthenticationRepository(db)

    async def create_user(self, user_data: UserCreateSchema) -> BaseUserSchema:
        user = await self.repo.create_user(user_data.username, user_data.password)
        log.info(f'User created with name: {user.username}')
        return BaseUserSchema.model_validate(user)
