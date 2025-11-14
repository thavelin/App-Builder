"""
Main FastAPI application entry point.
"""
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import generate, auth, websockets
from app.models import init_db
from app.config import settings
from app.services.job_timeout import start_job_timeout_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Initialize database
    await init_db()
    
    # Start background task to monitor stuck jobs
    await start_job_timeout_monitor(timeout_minutes=15)
    
    yield
    # Shutdown: Cleanup if needed
    pass


app = FastAPI(
    title="AI App Builder API",
    description="Multi-agent system for generating applications from natural language prompts",
    version="0.1.0",
    lifespan=lifespan
)

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import datetime
        import sys
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"\n[{timestamp}] {request.method} {request.url.path}", flush=True)
        sys.stdout.flush()
        if request.url.query:
            print(f"  Query: {request.url.query}", flush=True)
            sys.stdout.flush()
        try:
            response = await call_next(request)
            print(f"  → Status: {response.status_code}", flush=True)
            sys.stdout.flush()
            return response
        except Exception as e:
            print(f"  → ERROR: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            raise

app.add_middleware(RequestLoggingMiddleware)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(websockets.router, prefix="/api", tags=["websockets"])

# Mount static files for serving generated ZIP files
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)  # Ensure output directory exists
app.mount(
    "/downloads",
    StaticFiles(directory=str(output_dir)),
    name="downloads"
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "AI App Builder API is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

