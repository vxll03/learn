from typing import Annotated, TypeAlias

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.service import TokenService, UserService
from src.config.db import get_session


DatabaseDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]


def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)


def get_token_service() -> TokenService:
    return TokenService()


UserServiceDep: TypeAlias = Annotated[UserService, Depends(get_user_service)]
TokenServiceDep: TypeAlias = Annotated[TokenService, Depends(get_token_service)]
