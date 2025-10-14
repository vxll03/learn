from datetime import datetime, timedelta
from enum import Enum
import logging
from typing import Any
from fastapi import HTTPException
from passlib.context import CryptContext
from .env import settings
import jwt

log = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class PasswordHasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
    

class JwtToken:
    class TokenType(Enum):
        ACCESS = 'Access'
        REFRESH = 'Refresh'

    @staticmethod
    def create_token(token_data: dict[str, Any], type: TokenType):
        data = token_data.copy()
        data.update({'type': type.value})
        if type == JwtToken.TokenType.ACCESS:
            data.update({'exp': datetime.now() + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MIN)})
        elif type == JwtToken.TokenType.REFRESH:
            data.update({'exp': datetime.now() + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAY)})
        else:
            log.error(f'Unhandled token type: {type}')
            raise HTTPException(403, 'Error while authorize')
        try:
            return jwt.encode(data, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
        except jwt.PyJWTError as e:
            log.error(f'Error while encoding token: {e}')
            raise HTTPException(403, 'Incorrect token data')

    @staticmethod
    def decode_token(token) -> dict:
        try:
            return jwt.decode(token, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
        except jwt.PyJWTError as e:
            log.error(f'Error while decoding token: {e}')
            raise HTTPException(403, 'Incorrect token')