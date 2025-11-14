"""
WebSocket routes for real-time updates.
"""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.routes.generate import manager

router = APIRouter()


@router.websocket("/ws/jobs")
async def websocket_jobs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job list updates.
    
    Broadcasts updates when jobs are created, updated, or completed.
    """
    await manager.connect(websocket, "job_list")
    
    try:
        # Keep connection alive
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for job list", flush=True)
        manager.disconnect(websocket, "job_list")
    except Exception as e:
        print(f"WebSocket error for job list: {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        try:
            manager.disconnect(websocket, "job_list")
        except:
            pass

