import logging

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from src.auth.dependencies import TokenServiceDep, UserServiceDep, DatabaseDep
from src.auth.schemas import SelfUserSchema, UserCreateSchema, UserLoginSchema, UserUpdateSchema, UserResponseSchema

log = logging.getLogger(__name__)

general_router = APIRouter()
user_router = APIRouter()
token_router = APIRouter()


@general_router.get('/check/')
async def health_check(db: DatabaseDep) -> Response:
    if await db.scalar(select(1)):
        log.debug('Health check passed')
        return Response('success')
    return Response('fail', 503)


# User router section
@user_router.get('/me/', response_model=SelfUserSchema)
async def get_self_user(request: Request, service: UserServiceDep):
    return await service.get_or_404(request.auth.id)


@user_router.get('/{user_id}/', response_model=UserResponseSchema)
async def get_user_by_id(user_id: int, service: UserServiceDep):
    return await service.get_or_404(user_id)


@user_router.post('/', response_model=UserResponseSchema, status_code=201)
async def create_user(user_data: UserCreateSchema, service: UserServiceDep):
    return await service.create_user(user_data)


@user_router.patch('/{user_id}/', response_model=UserResponseSchema)
async def update_user(update_fields: UserUpdateSchema, user_id: int, service: UserServiceDep):
    return await service.update_user(user_id, update_fields)


@user_router.delete('/{user_id}/')
async def deactivate_user(user_id: int, service: UserServiceDep) -> bool:
    return await service.deactivate_user(user_id)


# Token router section
@token_router.post('/create/', status_code=204)
async def create_token(credentials: UserLoginSchema, token_service: TokenServiceDep):
    return await token_service.create_token(credentials)


@token_router.post('/refresh/', status_code=204)
async def refresh_token(request: Request, token_service: TokenServiceDep):
    return await token_service.update_token(request)


@token_router.post('/delete/', status_code=204)
async def delete_token(request: Request, token_service: TokenServiceDep) -> Response:
    return await token_service.delete_token(request)
