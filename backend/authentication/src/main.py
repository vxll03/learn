import logging

from fastapi import APIRouter, FastAPI

from src.logger import setup_logging
from src.auth.routes import user_router, token_router, general_router

setup_logging()
log = logging.getLogger(__name__)

app = FastAPI(
    title='Authentication',
    description='Authentication API documentation',
    version='1.0.0',
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    dependency_overrides={},
)

app_router = APIRouter(prefix='/api/v1')
app_router.include_router(general_router, tags=['General'], prefix='')
app_router.include_router(user_router, tags=['User'], prefix='/users')
app_router.include_router(token_router, tags=['Token'], prefix='/token')


app.include_router(app_router)
