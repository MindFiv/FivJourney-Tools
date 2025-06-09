from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# 创建异步数据库引擎
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite异步连接
    database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
elif settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL异步连接
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    # 默认使用SQLite
    database_url = "sqlite+aiosqlite:///./travel_tracker.db"

engine = create_async_engine(database_url, echo=settings.DEBUG, future=True)

# 创建异步会话制造器
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

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
