"""
Pydantic response schemas for API endpoints.
"""
from typing import Optional
from pydantic import BaseModel, Field


class GenerateResponse(BaseModel):
    """Response schema for app generation endpoint."""
    
    job_id: str = Field(
        ...,
        description="Unique identifier for the generation job",
        example="550e8400-e29b-41d4-a716-446655440000"
    )


class StatusResponse(BaseModel):
    """Response schema for job status endpoint."""
    
    job_id: str = Field(..., description="Unique identifier for the generation job")
    status: str = Field(
        ...,
        description="Current status: pending, in_progress, complete, failed",
        example="in_progress"
    )
    step: str = Field(
        ...,
        description="Current step: initializing, design, coding, reviewing, validating, packaging, deploying, complete",
        example="coding"
    )
    download_url: Optional[str] = Field(
        None,
        description="URL to download the generated app ZIP file",
        example="/downloads/550e8400-e29b-41d4-a716-446655440000.zip"
    )
    github_url: Optional[str] = Field(
        None,
        description="URL to the GitHub repository",
        example="https://github.com/username/app-builder-550e8400"
    )
    deployment_url: Optional[str] = Field(
        None,
        description="URL to the deployed application",
        example="https://app-builder-550e8400.vercel.app"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the job failed",
        example=None
    )


class JobListItem(BaseModel):
    """Response schema for job list items."""
    
    id: str = Field(..., description="Unique identifier for the generation job")
    prompt: str = Field(..., description="User's original prompt")
    status: str = Field(..., description="Current job status")
    step: str = Field(..., description="Current step in the generation process")
    created_at: Optional[str] = Field(None, description="Job creation timestamp (ISO format)")
    updated_at: Optional[str] = Field(None, description="Job last update timestamp (ISO format)")

