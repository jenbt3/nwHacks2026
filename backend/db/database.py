import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 1. Define the directory and ensure it exists
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Points to /backend
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True) # Creates /data if missing

# 2. Use the absolute path for the SQLite URL
DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR}/bridge.db"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session