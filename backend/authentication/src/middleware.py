import logging

from fastapi import Request
from src.auth.dependencies import DatabaseDep
from starlette.middleware.base import BaseHTTPMiddleware

log = logging.getLogger(__name__)


# class DBSessionMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app, db: DatabaseDep):
#         super().__init__(app)
#         self._session = db
#
#     async def dispatch(self, request: Request, call_next):
#         request.state.db = self._session
#         return await call_next(request)