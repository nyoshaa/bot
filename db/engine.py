__all__ = [
    "async_session_maker",
    "async_create_table",
]

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from .models import Base

engine: AsyncEngine = create_async_engine(url="sqlite+aiosqlite:///instance/sqlite.db", echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Создание таблицы в sqlite БД
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
async def async_create_table():
    """Создает таблицы в sqlite БД."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
