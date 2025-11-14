"""
Async database storage for jobs using SQLModel and SQLAlchemy.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import Job, AsyncSessionLocal


async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get a job by ID from the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        return {
            "id": job.id,
            "prompt": job.prompt,
            "status": job.status,
            "step": job.step,
            "download_url": job.download_url,
            "github_url": job.github_url,
            "deployment_url": job.deployment_url,
            "error": job.error,
            "user_id": job.user_id,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }


async def set_job(job_id: str, job_data: Dict[str, Any]) -> None:
    """Create or update a job in the database."""
    async with AsyncSessionLocal() as session:
        # Check if job exists
        result = await session.execute(select(Job).where(Job.id == job_id))
        existing_job = result.scalar_one_or_none()
        
        if existing_job:
            # Update existing job
            for key, value in job_data.items():
                if hasattr(existing_job, key) and key != "id":  # Don't update ID
                    setattr(existing_job, key, value)
            existing_job.updated_at = datetime.utcnow()
            session.add(existing_job)
        else:
            # Create new job
            new_job = Job(
                id=job_id,
                prompt=job_data.get("prompt", ""),
                status=job_data.get("status", "pending"),
                step=job_data.get("step", "initializing"),
                download_url=job_data.get("download_url"),
                github_url=job_data.get("github_url"),
                deployment_url=job_data.get("deployment_url"),
                error=job_data.get("error"),
                user_id=job_data.get("user_id"),
            )
            session.add(new_job)
        
        await session.commit()


async def update_job(
    job_id: str,
    status: Optional[str] = None,
    step: Optional[str] = None,
    download_url: Optional[str] = None,
    github_url: Optional[str] = None,
    deployment_url: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """Update specific fields of a job."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return
        
        if status is not None:
            job.status = status
        if step is not None:
            job.step = step
        if download_url is not None:
            job.download_url = download_url
        if github_url is not None:
            job.github_url = github_url
        if deployment_url is not None:
            job.deployment_url = deployment_url
        if error is not None:
            job.error = error
        
        job.updated_at = datetime.utcnow()
        session.add(job)
        await session.commit()


async def job_exists(job_id: str) -> bool:
    """Check if a job exists in the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none() is not None


async def list_jobs(
    limit: int = 50, 
    offset: int = 0, 
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List jobs, ordered by created_at descending. Optionally filter by user, status, or search."""
    async with AsyncSessionLocal() as session:
        query = select(Job)
        
        # Filter by user if provided
        if user_id:
            query = query.where(Job.user_id == user_id)
        
        # Filter by status if provided
        if status:
            query = query.where(Job.status == status)
        
        # Search in prompt if provided
        if search:
            query = query.where(Job.prompt.contains(search))
        
        result = await session.execute(
            query
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        jobs = result.scalars().all()
        
        return [
            {
                "id": job.id,
                "prompt": job.prompt,
                "status": job.status,
                "step": job.step,
                "download_url": job.download_url,
                "github_url": job.github_url,
                "deployment_url": job.deployment_url,
                "error": job.error,
                "user_id": job.user_id,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            }
            for job in jobs
        ]
