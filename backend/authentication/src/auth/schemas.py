from pydantic import BaseModel, Field, model_validator

from src.auth.models import Role


class BaseOrmSchema(BaseModel):
    model_config = {'from_attributes': True}


class BaseGroupSchema(BaseOrmSchema):
    name: str


class BaseUserSchema(BaseOrmSchema):
    username: str = Field(min_length=4)


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=8)
    password_retry: str = Field(min_length=8)

    @model_validator(mode='after')
    def validate_credentials(self):
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
