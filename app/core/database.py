import uuid
from typing import AsyncGenerator

from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings


class GUID(TypeDecorator):
    """平台无关的GUID类型，在SQLite中存储为String，在PostgreSQL中使用UUID"""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgreSQLUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(value)


# 创建异步数据库引擎
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite异步连接
    database_url = settings.DATABASE_URL.replace(
        "sqlite://", "sqlite+aiosqlite://"
    )
elif settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL异步连接
    database_url = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
else:
    # 默认使用SQLite
    database_url = "sqlite+aiosqlite:///./fivjourney_tools.db"

engine = create_async_engine(database_url, echo=settings.DEBUG, future=True)

# 创建异步会话制造器
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# 创建基础模型类
Base = declarative_base()


# 数据库依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 创建所有表
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
