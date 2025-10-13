import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.db import async_session

log = logging.getLogger(__name__)


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with async_session() as session:
            request.state.db = session
            try:
                response: Response = await call_next(request)
                if request.state.db.is_active:
                    await request.state.db.commit()

                return response
            except Exception as session_error:
                log.error(f'Error with database session occured: {session_error}')
                try:
                    if request.state.db.is_active:
                        await request.state.db.rollback()
                except Exception as rollback_error:
                    log.error(f'Error during rollback: {rollback_error}')

                raise
            finally:
                try:
                    await request.state.db.close()
                except Exception as close_error:
                    log.error(f'Error during close: {close_error}')
