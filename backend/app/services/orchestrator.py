"""
Orchestrator Service

Multi-agent workflow controller that coordinates the entire generation process.
"""
import asyncio
from typing import Dict, Any
from app.agents.project_manager import ProjectManagerAgent
from app.services.execution import ExecutionService
from app.services.github import GitHubService
from app.storage import update_job


class Orchestrator:
    """
    Orchestrates the multi-agent workflow:
    1. Project Manager breaks down prompt
    2. Specialist agents generate components
    3. Reviewer evaluates and iterates
    4. Execution service validates and packages
    5. GitHub service pushes to repository
    """
    
    def __init__(self):
        self.project_manager = ProjectManagerAgent()
        self.execution_service = ExecutionService()
        self.github_service = GitHubService()
    
    async def generate_app(self, job_id: str, prompt: str):
        """
        Main orchestration method for app generation.
        
        Updates job status throughout the process.
        """
        try:
            # Update status: design phase
            self._update_job_status(job_id, "in_progress", "design")
            
            # Step 1: Project Manager coordinates generation
            result = await self.project_manager.coordinate_generation(prompt)
            
            if not result["approved"]:
                self._update_job_status(
                    job_id,
                    "failed",
                    "reviewing",
                    error="Generation did not meet quality standards"
                )
                return
            
            # Update status: coding phase
            self._update_job_status(job_id, "in_progress", "coding")
            
            # Step 2: Prepare project files
            project_files = self._prepare_project_files(result["results"])
            
            # Step 3: Validate and package
            self._update_job_status(job_id, "in_progress", "validating")
            
            validation_result = await self.execution_service.validate_app_runs(project_files)
            if not validation_result["valid"]:
                self._update_job_status(
                    job_id,
                    "failed",
                    "validating",
                    error=validation_result.get("error", "Validation failed")
                )
                return
            
            # Step 4: Create ZIP package
            self._update_job_status(job_id, "in_progress", "packaging")
            zip_path = await self.execution_service.zip_project_output(project_files, job_id)
            
            # Update with download URL (in production, upload to S3 or similar)
            self._update_job_status(
                job_id,
                "in_progress",
                "deploying",
                download_url=f"/downloads/{job_id}.zip"
            )
            
            # Step 5: Push to GitHub (optional)
            try:
                github_result = await self.github_service.create_and_push_repo(
                    project_files=project_files,
                    job_id=job_id,
                    prompt=prompt
                )
                
                if github_result["success"]:
                    self._update_job_status(
                        job_id,
                        "in_progress",
                        "deploying",
                        github_url=github_result.get("repo_url")
                    )
            except Exception as e:
                # GitHub failure shouldn't block completion
                print(f"GitHub integration failed: {e}")
            
            # Step 6: Trigger deployment (placeholder)
            # deployment_url = await self.github_service.trigger_deploy(job_id)
            
            # Complete
            self._update_job_status(
                job_id,
                "complete",
                "complete",
                deployment_url=None  # TODO: Add actual deployment URL
            )
            
        except Exception as e:
            self._update_job_status(
                job_id,
                "failed",
                "error",
                error=str(e)
            )
    
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
    
    def _update_job_status(
        self,
        job_id: str,
        status: str,
        step: str,
        download_url: str = None,
        github_url: str = None,
        deployment_url: str = None,
        error: str = None
    ):
        """
        Update job status using shared storage.
        
        In production, this would update a database.
        """
        from app.storage import get_job
        
        # Get current job to preserve existing URLs
        current_job = get_job(job_id) or {}
        
        update_job(
            job_id=job_id,
            status=status,
            step=step,
            download_url=download_url or current_job.get("download_url"),
            github_url=github_url or current_job.get("github_url"),
            deployment_url=deployment_url or current_job.get("deployment_url"),
            error=error
        )

