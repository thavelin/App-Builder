"""
Unit tests for the storage module.
"""
import pytest
import asyncio
from app.storage import get_job, set_job, update_job, job_exists, list_jobs
from app.models import init_db, async_engine
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="function")
async def setup_db():
    """Set up test database."""
    await init_db()
    yield
    # Cleanup: drop all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: sync_conn.execute("DROP TABLE IF EXISTS jobs"))


@pytest.mark.asyncio
async def test_set_and_get_job(setup_db):
    """Test creating and retrieving a job."""
    job_id = "test-job-123"
    job_data = {
        "prompt": "Test prompt",
        "status": "pending",
        "step": "initializing",
        "download_url": None,
        "github_url": None,
        "deployment_url": None,
        "error": None,
    }
    
    await set_job(job_id, job_data)
    retrieved = await get_job(job_id)
    
    assert retrieved is not None
    assert retrieved["id"] == job_id
    assert retrieved["prompt"] == "Test prompt"
    assert retrieved["status"] == "pending"


@pytest.mark.asyncio
async def test_update_job(setup_db):
    """Test updating a job."""
    job_id = "test-job-456"
    job_data = {
        "prompt": "Test prompt",
        "status": "pending",
        "step": "initializing",
    }
    
    await set_job(job_id, job_data)
    await update_job(job_id, status="in_progress", step="coding")
    
    retrieved = await get_job(job_id)
    assert retrieved["status"] == "in_progress"
    assert retrieved["step"] == "coding"


@pytest.mark.asyncio
async def test_job_exists(setup_db):
    """Test checking if a job exists."""
    job_id = "test-job-789"
    
    assert await job_exists(job_id) is False
    
    await set_job(job_id, {"prompt": "Test", "status": "pending", "step": "initializing"})
    
    assert await job_exists(job_id) is True


@pytest.mark.asyncio
async def test_list_jobs(setup_db):
    """Test listing jobs."""
    # Create multiple jobs
    for i in range(5):
        await set_job(
            f"test-job-{i}",
            {
                "prompt": f"Test prompt {i}",
                "status": "pending",
                "step": "initializing",
            }
        )
    
    jobs = await list_jobs(limit=10)
    assert len(jobs) == 5
    
    # Test pagination
    jobs_limited = await list_jobs(limit=2)
    assert len(jobs_limited) == 2

