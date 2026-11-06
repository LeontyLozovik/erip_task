from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from exchange.config.settings import settings

DB_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DB_URL, echo=True)

AsyncSessionFabric = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFabric() as session:
        yield session
