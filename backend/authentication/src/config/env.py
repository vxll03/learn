import logging

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MIN: PositiveInt = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAY: PositiveInt = Field(default=7)
    ALGORITHM: str = Field(default='SHA256')
    JWT_ISSUER: str = Field(default='user_service')


class DatabaseSettings(BaseSettings):
    HOST: str = Field(default='127.0.0.1')
    PORT: int = Field(default=5432)
    USER: str = Field(default='postgres')
    PASS: str = Field(default='postgres')
    NAME: str = Field(default='auth')

    @property
    def DATABASE_URL(self):
        return f'postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}'

    @property
    def SYNC_DATABASE_URL(self):
        return f'postgresql+psycopg2://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}'


class Logging(BaseSettings):
    LEVEL: str = Field(default='DEBUG')

    @property
    def LOGGING_NAME(self):
        return logging.getLevelNamesMapping().get(self.LEVEL, logging.DEBUG)


class RedisSettings(BaseSettings):
    HOST: str = Field(default='127.0.0.1')
    PORT: int = Field(default=6379)
    DB: int = Field(default=0)

class Settings(BaseSettings):
    auth: AuthSettings = Field(default_factory=AuthSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    log: Logging = Field(default_factory=Logging)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(env_file='.env', extra='ignore', env_nested_delimiter='__')


settings = Settings()  # type: ignore
