"""
Pydantic request schemas for API endpoints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """Schema for file attachments."""
    
    name: str = Field(..., description="Name of the attached file")
    type: str = Field(..., description="MIME type of the file")
    content: str = Field(..., description="Base64-encoded file content")


class GenerateRequest(BaseModel):
    """Request schema for app generation endpoint."""
    
    prompt: str = Field(
        ...,
        description="Natural language description of the app to generate",
        min_length=10,
        max_length=2000,
        example="Create a todo list app with add, edit, and delete functionality"
    )
    
    review_threshold: int = Field(
        80,
        ge=0,
        le=100,
        description="Minimum score (0-100) needed for reviewer approval. Higher values mean stricter reviews."
    )
    
    attachments: Optional[List[Attachment]] = Field(
        None,
        description="Optional list of attached files (images, documents, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a simple calculator app with basic arithmetic operations",
                "review_threshold": 80,
                "attachments": None
            }
        }

