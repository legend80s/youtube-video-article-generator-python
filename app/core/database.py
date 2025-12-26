from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


sqlite_file_name = "hero_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
async_sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)

async_engine = create_async_engine(
    async_sqlite_url, echo=True, future=True, connect_args=connect_args
)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(async_engine)


async def create_db_and_tables():
    """初始化数据库（创建表）"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# 异步会话工厂
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
