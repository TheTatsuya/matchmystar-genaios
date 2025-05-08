from typing import Annotated, AsyncGenerator

from fastapi import Depends
from src.core.settings import get_settings
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

settings = get_settings()

engine = create_async_engine(
    settings.SQLALCHEMY_ASYNC_DATABASE_URI,
    poolclass=NullPool,
    future=True,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator:
    async with async_session() as session:
        yield session


AsyncDBSession = Annotated[AsyncSession, Depends(get_db)]
