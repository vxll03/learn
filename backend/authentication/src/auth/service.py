from datetime import datetime, timedelta
import logging
from uuid import uuid4

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import BaseUserSchema, JwtTokenSchema, SelfUserSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema
from src.config.env import settings
from src.config.security import JwtToken, PasswordHasher

log = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def get_user_by_credentials(self, credentials: UserLoginSchema) -> User:
        db_user = await self.repo.get_user_by_username(credentials.username)
        if not db_user:
            log.warning(f'User not found with name: {credentials.username}')
            raise HTTPException(404, 'User not found')
        
        is_correct = PasswordHasher.verify_password(credentials.password, db_user.password)
        if not is_correct:
            log.warning(f'Incorrect credentials for user: {credentials.username}')
            raise HTTPException(401, 'Incorrect credentials')

        return db_user


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


class TokenService:
    def __init__(self) -> None:
        pass

    def encode_token_data(self, user: User, has_refresh: bool):
        token_data = {'username': user.username, 'sub': user.id,}
        access_token = JwtToken.create_token(token_data, JwtToken.TokenType.ACCESS)
        refresh_token = None
        if has_refresh:
            refresh_token = JwtToken.create_token(token_data, JwtToken.TokenType.REFRESH)

        return JwtTokenSchema(access=access_token, refresh=refresh_token)

    def generate_cookie_response(self, token_schema: JwtTokenSchema):
        response = Response()
        response.set_cookie(
            key='access',
            value=token_schema.access,
            max_age=settings.auth.ACCESS_TOKEN_EXPIRE_MIN * 60,
            httponly=True,
            samesite='lax',
        )
        if token_schema.refresh:
            response.set_cookie(
                key='refresh',
                value=token_schema.refresh,
                max_age=settings.auth.REFRESH_TOKEN_EXPIRE_DAY * 60 * 60 * 24,
                httponly=True,
                samesite='lax',
            )

        return response
