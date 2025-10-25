import logging
from datetime import timedelta

from fastapi import HTTPException, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.schemas import (
    JwtTokenSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserUpdateSchema,
)
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

    async def get_or_404(self, user_id) -> User:
        db_user = await self.repo.get_user(user_id)
        if not db_user:
            log.warning(f'User not found with id: {user_id}')
            raise HTTPException(404, 'User not found')
        return db_user

    async def get_user_by_id(self, user_id) -> User:
        return await self.get_or_404(user_id)

    async def get_self_user(self, user_id) -> User:
        db_user = await self.repo.get_user_eager(user_id)
        if not db_user:
            log.warning(f'User not found with id: {user_id}')
            raise HTTPException(404, 'User not found')
        return db_user

    async def create_user(self, user_data: UserCreateSchema) -> User:
        password_hash = PasswordHasher.get_password_hash(user_data.password)
        user = await self.repo.create_user(user_data.username, password_hash)
        log.info(f'User created with name: {user.username}')
        return user

    async def update_user(self, user_id: int, update_fields: UserUpdateSchema) -> User:
        db_user = await self.get_or_404(user_id)
        db_user = await self.repo.update_user(db_user, **update_fields.model_dump(exclude_unset=True))
        return db_user

    async def deactivate_user(self, user_id: int) -> bool:
        db_user = await self.get_or_404(user_id)
        is_deactivated = await self.repo.deactivate_user(db_user)
        return is_deactivated


class TokenService:
    def __init__(self, redis: Redis, user_service: UserService) -> None:
        self.redis = redis
        self.user_service = user_service

    async def create_token(self, credentials: UserLoginSchema):
        db_user = await self.user_service.get_user_by_credentials(credentials)
        token_schema = self._encode_token_data(db_user, True)
        await self._set_redis_session(token_schema, db_user)
        response = self._generate_cookie_response(token_schema)
        return response

    async def update_token(self, request):
        refresh_token = request.cookies.get('refresh')
        if not refresh_token:
            raise HTTPException(401, 'Invalid refresh token')

        access_token = request.cookies.get('access')
        if access_token:
            await self._set_redis_blacklist(access_token, JwtToken.TokenType.ACCESS)

        decoded_refresh_token = JwtToken.decode_token(refresh_token, JwtToken.TokenType.REFRESH)
        db_user = await self.user_service.get_self_user(int(decoded_refresh_token.get('sub')))
        token_schema = self._encode_token_data(db_user, False)
        await self._set_redis_session(token_schema, db_user)
        response = self._generate_cookie_response(token_schema)
        return response

    async def delete_token(self, request):
        refresh_token = request.cookies.get('refresh')
        access_token = request.cookies.get('access')
        if access_token:
            await self._set_redis_blacklist(access_token, JwtToken.TokenType.ACCESS)

        if refresh_token:
            await self._set_redis_blacklist(refresh_token, JwtToken.TokenType.REFRESH)

        response = Response()
        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response

    async def _set_redis_session(self, token_schema: JwtTokenSchema, db_user: User):
        key = f'session:{token_schema.jti}'
        await self.redis.hset(key, 'user_id', str(db_user.id))
        await self.redis.hset(key, 'groups', ','.join([group.name for group in db_user.groups]))
        await self.redis.hset(key, 'role', db_user.role.value)
        await self.redis.expire(key, timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MIN))

    async def _set_redis_blacklist(self, token, token_type: JwtToken.TokenType):
        decoded_token = JwtToken.decode_token(token, token_type)
        key = f'blacklist:{decoded_token["jti"]}'
        await self.redis.set(key, str(True))
        await self.redis.expire(
            key, settings.auth.ACCESS_TOKEN_EXPIRE_MIN
        ) if token_type == JwtToken.TokenType.ACCESS else await self.redis.expire(
            key, settings.auth.REFRESH_TOKEN_EXPIRE_DAY
        )

    def _encode_token_data(self, user: User, has_refresh: bool):
        token_data = {
            'username': user.username,
            'sub': str(user.id),
        }
        access_token, jti = JwtToken.create_token(token_data, JwtToken.TokenType.ACCESS)
        refresh_token = None
        if has_refresh:
            refresh_token, _ = JwtToken.create_token(token_data, JwtToken.TokenType.REFRESH)

        return JwtTokenSchema(access=access_token, refresh=refresh_token, jti=jti)

    def _generate_cookie_response(self, token_schema: JwtTokenSchema):
        response = Response(status_code=204)
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
