import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .env import settings

log = logging.getLogger(__name__)

engine = create_async_engine(settings.db.DATABASE_URL)
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as session_error:
            # log.error(f'Error with database session occurred: {session_error}')
            try:
                await session.rollback()
            except Exception as rollback_error:
                # log.error(f'Error with database rollback occurred: {rollback_error}')
                await session.close()
            finally:
                raise
        finally:
            try:
                await session.close()
            except Exception as close_error:
                # log.error(f'Error with database session close occurred: {close_error}')
                raise


class Base(DeclarativeBase):
    pass
