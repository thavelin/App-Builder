"""
Database models using SQLModel.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker


class Job(SQLModel, table=True):
    """Job model for storing app generation jobs."""
    
    __tablename__ = "jobs"
    
    id: str = Field(primary_key=True, description="Unique job identifier (UUID)")
    prompt: str = Field(description="User's original prompt")
    status: str = Field(default="pending", description="Job status: pending, in_progress, complete, failed")
    step: str = Field(default="initializing", description="Current step in the generation process")
    download_url: Optional[str] = Field(default=None, description="URL to download the generated app ZIP")
    github_url: Optional[str] = Field(default=None, description="URL to the GitHub repository")
    deployment_url: Optional[str] = Field(default=None, description="URL to the deployed application")
    error: Optional[str] = Field(default=None, description="Error message if the job failed")
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", description="User who created this job")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Job last update timestamp")


class User(SQLModel, table=True):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id: Optional[str] = Field(default=None, primary_key=True, description="Unique user identifier (UUID)")
    email: str = Field(unique=True, index=True, description="User email address")
    username: str = Field(unique=True, index=True, description="Username")
    hashed_password: str = Field(description="Hashed password")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Account last update timestamp")


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./app_builder.db"

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize the database and create tables."""
    from sqlalchemy import inspect
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
