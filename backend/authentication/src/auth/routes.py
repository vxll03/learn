import logging

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from src.auth.dependencies import UserServiceDep
from src.auth.schemas import BaseUserSchema, SelfUserSchema, UserCreateSchema, UserUpdateSchema

log = logging.getLogger(__name__)

general_router = APIRouter()
user_router = APIRouter()
token_router = APIRouter()


@general_router.get('/check/')
async def health_check(request: Request) -> Response:
    if await request.state.db.scalar(select(1)):
        return Response('success')
    return Response('fail', 503)


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


@token_router.post('/create/')
async def create_token(): ...


@token_router.post('/refresh/')
async def refresh_token(): ...


@token_router.post('/delete/')
async def delete_token(): ...
