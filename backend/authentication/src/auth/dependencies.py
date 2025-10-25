from typing import Annotated, TypeAlias

from fastapi import Depends, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import TokenService, UserService
from src.config.db import get_session, get_redis

DatabaseDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
RedisDep: TypeAlias = Annotated[Redis, Depends(get_redis)]

def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)
UserServiceDep: TypeAlias = Annotated[UserService, Depends(get_user_service)]


def get_token_service(redis: RedisDep, user_service: UserServiceDep) -> TokenService:
    return TokenService(redis, user_service)
TokenServiceDep: TypeAlias = Annotated[TokenService, Depends(get_token_service)]


