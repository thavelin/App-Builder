"""
Shared job storage.

In production, replace this with a database (PostgreSQL, Redis, etc.).
"""
from typing import Dict, Any, Optional

# In-memory job storage
_jobs: Dict[str, Dict[str, Any]] = {}


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get a job by ID."""
    return _jobs.get(job_id)


def set_job(job_id: str, job_data: Dict[str, Any]) -> None:
    """Set or update a job."""
    _jobs[job_id] = job_data


def update_job(
    job_id: str,
    status: Optional[str] = None,
    step: Optional[str] = None,
    download_url: Optional[str] = None,
    github_url: Optional[str] = None,
    deployment_url: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """Update specific fields of a job."""
    if job_id not in _jobs:
        _jobs[job_id] = {}
    
    if status is not None:
        _jobs[job_id]["status"] = status
    if step is not None:
        _jobs[job_id]["step"] = step
    if download_url is not None:
        _jobs[job_id]["download_url"] = download_url
    if github_url is not None:
        _jobs[job_id]["github_url"] = github_url
    if deployment_url is not None:
        _jobs[job_id]["deployment_url"] = deployment_url
    if error is not None:
        _jobs[job_id]["error"] = error


def job_exists(job_id: str) -> bool:
    """Check if a job exists."""
    return job_id in _jobs

