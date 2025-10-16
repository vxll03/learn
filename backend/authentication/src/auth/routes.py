import logging

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from src.auth.dependencies import TokenServiceDep, UserServiceDep
from src.auth.schemas import BaseUserSchema, SelfUserSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema
from src.config.security import JwtToken

log = logging.getLogger(__name__)

general_router = APIRouter()
user_router = APIRouter()
token_router = APIRouter()


@general_router.get('/check/')
async def health_check(request: Request) -> Response:
    if await request.state.db.scalar(select(1)):
        return Response('success')
    return Response('fail', 503)


# User router section
@user_router.get('/me/', response_model=SelfUserSchema)
async def get_self_user(request: Request, service: UserServiceDep):
    return await service._get_or_404(request.auth.id)


@user_router.get('/{user_id}/', response_model=BaseUserSchema)
async def get_user_by_id(user_id: int, service: UserServiceDep):
    return await service._get_or_404(user_id)


@user_router.post('/create/', response_model=BaseUserSchema, status_code=201)
async def create_user(user_data: UserCreateSchema, service: UserServiceDep) -> BaseUserSchema:
    return await service.create_user(user_data)


@user_router.patch('/{user_id}/', response_model=BaseUserSchema)
async def update_user(update_fields: UserUpdateSchema, user_id: int, service: UserServiceDep) -> BaseUserSchema:
    return await service.update_user(user_id, update_fields)


@user_router.delete('/{user_id}/')
async def deactivate_user(user_id: int, service: UserServiceDep) -> bool:
    return await service.deactivate_user(user_id)


# Token router section 
@token_router.post('/create/', status_code=204)
async def create_token(credentials: UserLoginSchema, token_service: TokenServiceDep, user_service: UserServiceDep) -> Response: 
    db_user = await user_service.get_user_by_credentials(credentials)
    token_schema = token_service.encode_token_data(db_user, True)
    response = token_service.generate_cookie_response(token_schema)
    return response


@token_router.post('/refresh/', status_code=204)
async def refresh_token(request: Request, token_service: TokenServiceDep, user_service: UserServiceDep): 
    decoded_refresh_token = JwtToken.decode_token(request.cookies.get('refresh'), JwtToken.TokenType.REFRESH)
    db_user = await user_service._get_or_404(decoded_refresh_token.get('sub'))
    token_schema = token_service.encode_token_data(db_user, False)
    response = token_service.generate_cookie_response(token_schema)
    return response


@token_router.post('/delete/', status_code=204)
async def delete_token() -> Response: 
    response = Response()
    response.delete_cookie('access')
    response.delete_cookie('refresh')
    return response
