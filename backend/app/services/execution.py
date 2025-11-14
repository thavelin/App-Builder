"""
Execution Service

Handles sandbox/runner integration for validating generated code.
"""
import os
import zipfile
import tempfile
from typing import Dict, Any, List
from pathlib import Path


class ExecutionService:
    """
    Service for executing and validating generated code.
    
    Responsibilities:
    - Run generated code in a sandbox
    - Validate that the app runs correctly
    - Package the project into a ZIP file
    """
    
    def __init__(self):
        self.output_dir = Path("output")  # Directory for generated projects
        self.output_dir.mkdir(exist_ok=True)
    
    async def run_generated_code(self, project_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Run the generated code in a sandbox environment.
        
        TODO: Implement actual sandbox execution.
        For now, this is a placeholder that simulates execution.
        
        Returns a dictionary with execution results.
        """
        # TODO: Implement sandbox execution
        # - Create temporary directory
        # - Write files
        # - Run appropriate command (python, npm start, etc.)
        # - Capture output and errors
        # - Clean up
        
        return {
            "success": True,
            "output": "Code executed successfully (placeholder)",
            "errors": [],
            "exit_code": 0
        }
    
    async def validate_app_runs(self, project_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate that the generated app runs without critical errors.
        
        Returns a dictionary with validation results.
        """
        # TODO: Implement actual validation
        # - Check for syntax errors
        # - Verify dependencies are specified
        # - Run basic tests if applicable
        # - Check for common issues
        
        # Placeholder validation
        has_entry_point = any(
            "app.py" in path or "main.py" in path or "index.js" in path
            for path in project_files.keys()
        )
        
        return {
            "valid": has_entry_point,
            "errors": [] if has_entry_point else ["No entry point found"],
            "warnings": ["This is a placeholder validation"]
        }
    
    async def zip_project_output(
        self,
        project_files: Dict[str, str],
        job_id: str
    ) -> str:
        """
        Package the project files into a ZIP archive.
        
        Returns the path to the created ZIP file.
        """
        zip_path = self.output_dir / f"{job_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path, content in project_files.items():
                # Ensure proper path handling
                zipf.writestr(file_path, content)
        
        return str(zip_path)
    
    def _detect_project_type(self, project_files: Dict[str, str]) -> str:
        """
        Detect the type of project based on files present.
        
        Returns: 'python', 'node', 'react', etc.
        """
        file_paths = list(project_files.keys())
        
        if any("package.json" in path for path in file_paths):
            if any(".tsx" in path or ".jsx" in path for path in file_paths):
                return "react"
            return "node"
        elif any("requirements.txt" in path or ".py" in path for path in file_paths):
            return "python"
        elif any("Cargo.toml" in path for path in file_paths):
            return "rust"
        
        return "unknown"

