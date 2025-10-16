from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
from typing import Any
from uuid import uuid4
from fastapi import HTTPException
from passlib.context import CryptContext
from .env import settings
import jwt

log = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PasswordHasher:
    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password) -> str:
        return pwd_context.hash(password)


class JwtToken:
    class TokenType(Enum):
        ACCESS = 'Access'
        REFRESH = 'Refresh'

    @staticmethod
    def create_token(token_data: dict[str, Any], type: TokenType):
        now = datetime.now(timezone.utc)

        data = token_data.copy()
        data.update(
            {
                'iss': settings.auth.JWT_ISSUER,  # need to replace mb
                'type': type.value,
                'jti': str(uuid4()),
                'iat': now,
            }
        )
        if type == JwtToken.TokenType.ACCESS:
            data.update({'exp': now + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MIN)})
        elif type == JwtToken.TokenType.REFRESH:
            data.update({'exp': now + timedelta(days=settings.auth.REFRESH_TOKEN_EXPIRE_DAY)})
        else:
            log.error(f'Unhandled token type: {type}')
            raise HTTPException(403, 'Error while authorize')
        try:
            return jwt.encode(data, settings.auth.SECRET_KEY, settings.auth.ALGORITHM)
        except jwt.PyJWTError as e:
            log.error(f'Error while encoding token: {e}')
            raise HTTPException(403, 'Incorrect token data')

    @staticmethod
    def decode_token(token, token_type: TokenType) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.auth.SECRET_KEY,
                algorithms=[settings.auth.ALGORITHM],
                options=({'verify_exp': True, 'verify_aud': False})
            )
            if payload.get('type') != token_type.value:
                raise HTTPException(403, 'Invalid token type')

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, 'Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(403, 'Invalid token')
        except jwt.PyJWTError as e:
            log.error(f'Error while decoding token: {e}')
            raise HTTPException(403, 'Incorrect token')
