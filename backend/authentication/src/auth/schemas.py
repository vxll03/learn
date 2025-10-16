from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.auth.models import Role


class JwtTokenSchema(BaseModel):
    access: str
    refresh: Optional[str]
    model_config = ConfigDict(extra='ignore')


class BaseOrmSchema(BaseModel):
    model_config = ConfigDict(extra='ignore', from_attributes=True)


class BaseGroupSchema(BaseOrmSchema):
    name: str


class BaseUserSchema(BaseOrmSchema):
    username: str = Field(min_length=4)


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8)
    password_retry: str = Field(min_length=8)

    @model_validator(mode='after')
    def validate_credentials(self) -> 'UserCreateSchema':
        if self.password != self.password_retry:
            raise ValueError('Passwords need to be same')
        if self.password == self.username:
            raise ValueError('Password cannot be same as username')
        return self


class UserLoginSchema(BaseUserSchema):
    password: str


class SelfUserSchema(BaseUserSchema):
    id: int
    email: str
    role: Role
    groups: list[BaseGroupSchema]


class UserUpdateSchema(BaseOrmSchema):
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    password_retry: Optional[str] = Field(default=None, exclude=True)
    email: Optional[str] = Field(default=None)

    @model_validator(mode='after')
    def validate_password(self) -> 'UserUpdateSchema':
        if self.password and self.password != self.password_retry:
            raise ValueError('Passwords need to be the same')
        if self.password and len(self.password) < 8:
            raise ValueError('Password cannot be less than 8 char length')
        return self
