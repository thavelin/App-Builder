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
    from sqlalchemy import inspect, text
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
        
        # Migrate existing tables if needed
        # Check if jobs table exists and if user_id column is missing
        try:
            # Check if jobs table exists
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
            ))
            jobs_table_exists = result.scalar() is not None
            
            if jobs_table_exists:
                # Check if user_id column exists
                result = await conn.execute(text("PRAGMA table_info(jobs)"))
                columns = [row[1] for row in result.fetchall()]
                
                if 'user_id' not in columns:
                    print("[Database Migration] Adding user_id column to jobs table...", flush=True)
                    await conn.execute(text(
                        "ALTER TABLE jobs ADD COLUMN user_id TEXT"
                    ))
                    print("[Database Migration] ✓ user_id column added successfully", flush=True)
        except Exception as e:
            print(f"[Database Migration] Warning: Could not migrate jobs table: {e}", flush=True)
        
        # Check if users table exists, if not create it
        try:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            ))
            users_table_exists = result.scalar() is not None
            
            if not users_table_exists:
                print("[Database Migration] Creating users table...", flush=True)
                # Users table will be created by SQLModel.metadata.create_all above
                # But we ensure it exists here
                await conn.run_sync(SQLModel.metadata.create_all)
        except Exception as e:
            print(f"[Database Migration] Warning: Could not check/create users table: {e}", flush=True)


async def get_session() -> AsyncSession:
    """Get an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
