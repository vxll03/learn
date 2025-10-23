import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.db import Base, get_session
from src.main import app


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    """Асинхронный движок для SQLite"""
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def async_session_factory(async_engine):
    """Фабрика асинхронных сессий"""
    yield async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
    )


@pytest_asyncio.fixture
async def async_db_session(async_session_factory):
    """Асинхронная сессия с rollback для каждого теста"""
    async with async_session_factory() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()


@pytest_asyncio.fixture
async def client(async_db_session):
    def override_get_db():
        return async_db_session

    test_app = app
    test_app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url='http://test/api/v1') as ac:
        yield ac

    test_app.dependency_overrides.clear()