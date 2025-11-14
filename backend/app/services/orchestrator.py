"""
Orchestrator Service

Multi-agent workflow controller that coordinates the entire generation process.
"""
import asyncio
from typing import Dict, Any, Optional
from app.agents.project_manager import ProjectManagerAgent
from app.services.execution import ExecutionService
from app.services.github import GitHubService
from app.storage import update_job, get_job


class Orchestrator:
    """
    Orchestrates the multi-agent workflow:
    1. Project Manager breaks down prompt
    2. Specialist agents generate components
    3. Reviewer evaluates and iterates
    4. Execution service validates and packages
    5. GitHub service pushes to repository
    """
    
    def __init__(self, websocket_manager=None):
        self.project_manager = ProjectManagerAgent()
        self.execution_service = ExecutionService()
        self.github_service = GitHubService()
        self.websocket_manager = websocket_manager
    
    async def generate_app(self, job_id: str, prompt: str):
        """
        Main orchestration method for app generation.
        
        Updates job status throughout the process.
        Each step is wrapped in try/except to prevent silent failures.
        """
        import traceback
        
        # Step 1: Design phase
        try:
            await self._update_job_status(job_id, "in_progress", "design")
            result = await self.project_manager.coordinate_generation(prompt)
            
            if not result["approved"]:
                await self._update_job_status(
                    job_id,
                    "failed",
                    "reviewing",
                    error="Generation did not meet quality standards"
                )
                return
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error in design phase for job {job_id}:", flush=True)
            print(error_details, flush=True)
            await self._update_job_status(job_id, "failed", "design", error=f"Design phase error: {str(e)}")
            return
        
        # Step 2: Prepare project files
        try:
            await self._update_job_status(job_id, "in_progress", "coding")
            project_files = self._prepare_project_files(result["results"])
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error preparing project files for job {job_id}:", flush=True)
            print(error_details, flush=True)
            await self._update_job_status(job_id, "failed", "coding", error=f"File preparation error: {str(e)}")
            return
        
        # Step 3: Validate
        try:
            await self._update_job_status(job_id, "in_progress", "validating")
            validation_result = await self.execution_service.validate_app_runs(project_files)
            if not validation_result["valid"]:
                # Provide user-friendly error message for missing entrypoint
                error_message = validation_result.get("error", "Validation failed")
                if "No entry point found" in error_message:
                    error_message = "The generated app is missing a runnable file (e.g. app.py, main.py, index.js, or index.html). Please try again or refine your prompt."
                
                await self._update_job_status(
                    job_id,
                    "failed",
                    "validating",
                    error=error_message
                )
                return
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error in validation phase for job {job_id}:", flush=True)
            print(error_details, flush=True)
            await self._update_job_status(job_id, "failed", "validating", error=f"Validation error: {str(e)}")
            return
        
        # Step 4: Package
        try:
            await self._update_job_status(job_id, "in_progress", "packaging")
            zip_path = await self.execution_service.zip_project_output(project_files, job_id)
            await self._update_job_status(
                job_id,
                "in_progress",
                "deploying",
                download_url=f"/downloads/{job_id}.zip"
            )
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error in packaging phase for job {job_id}:", flush=True)
            print(error_details, flush=True)
            await self._update_job_status(job_id, "failed", "packaging", error=f"Packaging error: {str(e)}")
            return
        
        # Step 5: GitHub integration (optional, non-blocking)
        try:
            github_result = await self.github_service.create_and_push_repo(
                project_files=project_files,
                job_id=job_id,
                prompt=prompt
            )
            if github_result["success"]:
                await self._update_job_status(
                    job_id,
                    "in_progress",
                    "deploying",
                    github_url=github_result.get("repo_url")
                )
        except Exception as e:
            # GitHub failure shouldn't block completion
            print(f"GitHub integration failed for job {job_id}: {e}", flush=True)
        
        # Step 6: Complete
        try:
            await self._update_job_status(
                job_id,
                "complete",
                "complete",
                deployment_url=None  # TODO: Add actual deployment URL
            )
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error completing job {job_id}:", flush=True)
            print(error_details, flush=True)
            # Try to update status one more time
            try:
                await self._update_job_status(job_id, "failed", "error", error=f"Completion error: {str(e)}")
            except:
                pass
    
    def _prepare_project_files(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        Combine results from all agents into a structured project file dictionary.
        
        Returns a dictionary mapping file paths to file contents.
        """
        project_files = {}
        
        # Add code files
        if results.get("code") and results["code"].get("files"):
            for file_info in results["code"]["files"]:
                project_files[file_info["path"]] = file_info["content"]
        
        # Add UI files if any
        if results.get("ui"):
            # TODO: Convert UI design to actual component files
            pass
        
        return project_files
    
    async def _update_job_status(
        self,
        job_id: str,
        status: str,
        step: str,
        download_url: Optional[str] = None,
        github_url: Optional[str] = None,
        deployment_url: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Update job status using shared storage and broadcast via WebSocket.
        """
        # Get current job to preserve existing URLs
        current_job = await get_job(job_id) or {}
        
        await update_job(
            job_id=job_id,
            status=status,
            step=step,
            download_url=download_url or current_job.get("download_url"),
            github_url=github_url or current_job.get("github_url"),
            deployment_url=deployment_url or current_job.get("deployment_url"),
            error=error
        )
        
        # Broadcast update via WebSocket if manager is available
        if self.websocket_manager:
            try:
                await self.websocket_manager.broadcast_to_job(job_id, {
                    "type": "status_update",
                    "data": {
                        "job_id": job_id,
                        "status": status,
                        "step": step,
                        "download_url": download_url or current_job.get("download_url"),
                        "github_url": github_url or current_job.get("github_url"),
                        "deployment_url": deployment_url or current_job.get("deployment_url"),
                        "error": error
                    }
                })
            except Exception as e:
                # WebSocket errors shouldn't block job updates
                print(f"WebSocket broadcast error: {e}")

