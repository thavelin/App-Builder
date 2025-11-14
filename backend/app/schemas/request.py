"""
Pydantic request schemas for API endpoints.
"""
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request schema for app generation endpoint."""
    
    prompt: str = Field(
        ...,
        description="Natural language description of the app to generate",
        min_length=10,
        max_length=2000,
        example="Create a todo list app with add, edit, and delete functionality"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Create a simple calculator app with basic arithmetic operations"
            }
        }

