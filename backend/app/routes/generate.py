"""
API routes for app generation endpoints.
"""
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.request import GenerateRequest
from app.schemas.response import GenerateResponse, StatusResponse
from app.services.orchestrator import Orchestrator
from app.storage import get_job, set_job

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_app(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger app generation from a natural language prompt.
    
    Returns a job_id that can be used to poll for status.
    """
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    set_job(job_id, {
        "status": "pending",
        "step": "initializing",
        "prompt": request.prompt,
        "download_url": None,
        "github_url": None,
        "deployment_url": None,
        "error": None
    })
    
    # Start generation in background
    orchestrator = Orchestrator()
    background_tasks.add_task(orchestrator.generate_app, job_id, request.prompt)
    
    return GenerateResponse(job_id=job_id)


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Get the current status of a generation job.
    
    Returns current step, progress, and any available URLs.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        step=job["step"],
        download_url=job["download_url"],
        github_url=job["github_url"],
        deployment_url=job["deployment_url"],
        error=job.get("error")
    )

