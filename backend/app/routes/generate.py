"""
API routes for app generation endpoints.
"""
import uuid
import json
import asyncio
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from app.schemas.request import GenerateRequest
from app.schemas.response import GenerateResponse, StatusResponse, JobListItem
from app.services.orchestrator import Orchestrator
from app.storage import get_job, set_job, list_jobs

router = APIRouter()

# WebSocket connections manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Connect a WebSocket for a specific job."""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        """Disconnect a WebSocket."""
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending WebSocket message: {e}", flush=True)
            raise
    
    async def broadcast_to_job(self, job_id: str, message: dict):
        """Broadcast a message to all connections for a specific job."""
        if job_id in self.active_connections:
            connection_count = len(self.active_connections[job_id])
            print(f"[WebSocket] Broadcasting to {connection_count} connection(s) for job {job_id}", flush=True)
            disconnected = []
            sent_count = 0
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                    sent_count += 1
                except Exception as e:
                    print(f"[WebSocket] Failed to send to connection for job {job_id}: {e}", flush=True)
                    disconnected.append(connection)
            
            print(f"[WebSocket] Successfully sent to {sent_count}/{connection_count} connection(s) for job {job_id}", flush=True)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn, job_id)
        else:
            print(f"[WebSocket] No active connections for job {job_id}", flush=True)


manager = ConnectionManager()


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
    await set_job(job_id, {
        "status": "pending",
        "step": "initializing",
        "prompt": request.prompt,
        "download_url": None,
        "github_url": None,
        "deployment_url": None,
        "error": None
    })
    
    # Start generation in background
    orchestrator = Orchestrator(manager)
    background_tasks.add_task(orchestrator.generate_app, job_id, request.prompt)
    
    return GenerateResponse(job_id=job_id)


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """
    Get the current status of a generation job.
    
    Returns current step, progress, and any available URLs.
    """
    job = await get_job(job_id)
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


@router.get("/jobs", response_model=List[JobListItem])
async def get_jobs(limit: int = 50, offset: int = 0):
    """
    List all jobs with pagination.
    
    Returns a list of jobs ordered by creation date (newest first).
    """
    jobs = await list_jobs(limit=limit, offset=offset)
    return [
        JobListItem(
            id=job["id"],
            prompt=job["prompt"],
            status=job["status"],
            step=job["step"],
            created_at=job["created_at"],
            updated_at=job["updated_at"]
        )
        for job in jobs
    ]


@router.websocket("/ws/status/{job_id}")
async def websocket_status(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job status updates.
    
    Connects to a specific job and streams status changes.
    """
    await manager.connect(websocket, job_id)
    
    try:
        # Send initial status
        job = await get_job(job_id)
        if job:
            try:
                await manager.send_personal_message({
                    "type": "status_update",
                    "data": {
                        "job_id": job_id,
                        "status": job["status"],
                        "step": job["step"],
                        "download_url": job["download_url"],
                        "github_url": job["github_url"],
                        "deployment_url": job["deployment_url"],
                        "error": job.get("error")
                    }
                }, websocket)
            except Exception as send_error:
                print(f"Error sending initial status: {send_error}", flush=True)
                raise
        
        # Keep connection alive - check connection state periodically
        while True:
            await asyncio.sleep(1)
            # Check if connection is still open by trying to send a ping
            try:
                # FastAPI WebSocket doesn't have a direct state check, so we'll just continue
                # The exception will be raised if connection is closed
                pass
            except Exception:
                # Connection closed, break out of loop
                break
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for job {job_id}", flush=True)
        manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"WebSocket error for job {job_id}: {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        try:
            manager.disconnect(websocket, job_id)
        except:
            pass

