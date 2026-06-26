from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 1. Create the async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  
    future=True,
    connect_args={"ssl": "require"}  # <-- Native asyncpg SSL (this sends SNI!)
)

# 2. Create the session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Create the Base class for our ORM models to inherit from
Base = declarative_base()

# 4. Dependency to get a database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
