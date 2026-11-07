from collections.abc import AsyncGenerator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from exchange.config.settings import settings

DB_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=str(settings.DB_HOST),
    port=settings.DB_PORT,
    database=settings.POSTGRES_DB,
)

engine = create_async_engine(DB_URL, echo=True)

AsyncSessionFabric = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionFabric() as session:
        yield session
