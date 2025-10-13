import logging

from fastapi import FastAPI, Request, Response

from src.logger import setup_logging
from src.middleware import DBSessionMiddleware

setup_logging()
log = logging.getLogger(__name__)

app = FastAPI(
    title='Authentication',
    description='Authentication API documentation',
    root_path='/api/v1',
)
app.add_middleware(DBSessionMiddleware)


@app.get('/')
async def health_check(request: Request):
    log.info(request.state.db)
    if request.state.db:
        log.info('SUCCESS')
        return Response('success')
    return Response('failed')
