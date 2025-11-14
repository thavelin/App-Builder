"""
Background task to monitor and timeout stuck jobs.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from app.storage import list_jobs, update_job, get_job
from app.routes.generate import manager as websocket_manager


async def check_stuck_jobs(timeout_minutes: int = 15):
    """
    Background coroutine that checks for jobs stuck in 'in_progress' status
    for more than the specified timeout and marks them as failed.
    
    Args:
        timeout_minutes: Number of minutes before a job is considered stuck (default: 15)
    """
    while True:
        try:
            # Get all jobs
            jobs = await list_jobs(limit=1000, offset=0)
            timeout_delta = timedelta(minutes=timeout_minutes)
            now = datetime.utcnow()
            
            for job in jobs:
                # Only check jobs that are in progress
                if job["status"] != "in_progress":
                    continue
                
                # Parse updated_at timestamp
                updated_at_str = job.get("updated_at")
                if not updated_at_str:
                    continue
                
                try:
                    updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                    # Handle timezone-aware datetime
                    if updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                except (ValueError, AttributeError):
                    # If we can't parse the timestamp, skip this job
                    continue
                
                # Check if job has been stuck for too long
                if now - updated_at > timeout_delta:
                    print(f"Job {job['id']} has been stuck for more than {timeout_minutes} minutes. Marking as failed.", flush=True)
                    
                    # Update job status
                    await update_job(
                        job_id=job["id"],
                        status="failed",
                        step="timeout",
                        error="Job timed out after 15 minutes of inactivity."
                    )
                    
                    # Broadcast via WebSocket
                    try:
                        await websocket_manager.broadcast_to_job(job["id"], {
                            "type": "status_update",
                            "data": {
                                "job_id": job["id"],
                                "status": "failed",
                                "step": "timeout",
                                "error": "Job timed out after 15 minutes of inactivity.",
                                "download_url": job.get("download_url"),
                                "github_url": job.get("github_url"),
                                "deployment_url": job.get("deployment_url"),
                            }
                        })
                    except Exception as ws_error:
                        print(f"Failed to broadcast timeout status via WebSocket: {ws_error}", flush=True)
        
        except Exception as e:
            # Don't crash on database schema errors (e.g., during migration)
            error_msg = str(e)
            if "no such column" in error_msg.lower() or "operationalerror" in error_msg.lower():
                print(f"Error in stuck job checker (likely schema migration in progress): {error_msg[:200]}", flush=True)
            else:
                print(f"Error in stuck job checker: {e}", flush=True)
            import traceback
            traceback.print_exc()
        
        # Check every minute
        await asyncio.sleep(60)


async def start_job_timeout_monitor(timeout_minutes: int = 15):
    """
    Start the background task to monitor stuck jobs.
    
    Args:
        timeout_minutes: Number of minutes before a job is considered stuck (default: 15)
    """
    asyncio.create_task(check_stuck_jobs(timeout_minutes))

