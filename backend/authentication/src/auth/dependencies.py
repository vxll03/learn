from typing import Annotated

from fastapi import Depends, Request

from src.auth.service import UserService


def get_user_service(request: Request) -> UserService:
    return UserService(request.state.db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
