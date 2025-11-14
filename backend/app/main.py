"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import generate

app = FastAPI(
    title="AI App Builder API",
    description="Multi-agent system for generating applications from natural language prompts",
    version="0.1.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api", tags=["generate"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI App Builder API is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

