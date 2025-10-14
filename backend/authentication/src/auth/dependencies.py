from typing import Annotated

from fastapi import Depends, Request

from src.auth.service import AuthenticationService


def get_auth_service(request: Request) -> AuthenticationService:
    return AuthenticationService(request.state.db)


AuthService = Annotated[AuthenticationService, Depends(get_auth_service)]
