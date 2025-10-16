from typing import Annotated

from fastapi import Depends, Request

from src.auth.service import TokenService, UserService


def get_user_service(request: Request) -> UserService:
    return UserService(request.state.db)

def get_token_service() -> TokenService:
    return TokenService()


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]