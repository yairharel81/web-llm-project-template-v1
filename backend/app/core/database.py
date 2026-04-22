from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# pool_size + max_overflow sets the maximum number of DB connections.
# The defaults (5 + 10) exhaust quickly when running Playwright E2E tests that
# open multiple browser contexts with SSE connections alongside regular API
# requests. 20 + 30 is a safe ceiling for local dev and CI.
engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,
    pool_size=20,
    max_overflow=30,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
