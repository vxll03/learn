import logging
from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from src.auth.dependencies import AuthService
from src.auth.schemas import BaseUserSchema, UserCreateSchema

log = logging.getLogger(__name__)

general_router = APIRouter()
user_router = APIRouter()
token_router = APIRouter()

@general_router.get('/check/')
async def health_check(request: Request) -> Response:
    if await request.state.db.scalar(select(1)):
        return Response('success')
    return Response('fail')


@user_router.post('/create/', response_model=BaseUserSchema, status_code=201)
async def create_user(user_data: UserCreateSchema, service: AuthService) -> BaseUserSchema:
    return await service.create_user(user_data)

@user_router.post('/udpate/')
async def update_user(): ...

@user_router.post('/deactivate/')
async def deactivate_user(): ...



@token_router.post('/create/')
async def create_token(): ...


@token_router.post('/refresh/')
async def refresh_token(): ...


@token_router.post('/delete/')
async def delete_token(): ...
