import re
from datetime import timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.auth.models import Role


class JwtTokenSchema(BaseModel):
    access: str
    refresh: Optional[str]

    jti: str
    model_config = ConfigDict(extra='ignore')


class BaseOrmSchema(BaseModel):
    model_config = ConfigDict(extra='ignore', from_attributes=True)


class BaseGroupSchema(BaseOrmSchema):
    name: str


class BaseUserSchema(BaseOrmSchema):
    username: str = Field(min_length=4, max_length=50)


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8, max_length=50)
    password_retry: str = Field(min_length=8, max_length=50)

    @model_validator(mode='after')
    def validate_credentials(self) -> 'UserCreateSchema':
        if self.password != self.password_retry:
            raise ValueError('Passwords need to be same')
        if self.password == self.username:
            raise ValueError('Password cannot be same as username')
        return self


class UserLoginSchema(BaseUserSchema):
    password: str


class UserUpdateSchema(BaseOrmSchema):
    username: Optional[str] = Field(default=None, min_length=4, max_length=50)
    password: Optional[str] = Field(default=None, min_length=8, max_length=50)
    password_retry: Optional[str] = Field(default=None, exclude=True, min_length=8, max_length=50)
    email: Optional[str] = Field(default=None)

    @model_validator(mode='after')
    def validate_email(self) -> 'UserUpdateSchema':
        if self.email is None:
            return self
        if not re.search(r'[^@]+@[^@]{2,10}\.[^@]{1,4}$', self.email):
            raise ValueError('Invalid email')
        return self

    @model_validator(mode='after')
    def validate_password(self) -> 'UserUpdateSchema':
        if self.password and self.password != self.password_retry:
            raise ValueError('Passwords need to be the same')
        if self.password and len(self.password) < 8:
            raise ValueError('Password cannot be less than 8 char length')
        return self

class SelfUserSchema(BaseUserSchema):
    email: str
    role: Role
    groups: list[BaseGroupSchema]

class UserResponseSchema(BaseUserSchema):
    id: int
    email: Optional[str]