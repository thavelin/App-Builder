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
        Run the generated code in a sandbox environment using subprocess.
        
        NOTE: This is a basic implementation. For production, use proper sandboxing:
        - Docker containers with resource limits
        - Isolated execution environments
        - Timeout mechanisms
        - Security restrictions (no network access, limited file system, etc.)
        
        Returns a dictionary with execution results.
        """
        import asyncio
        import subprocess
        import tempfile
        import shutil
        
        project_type = self._detect_project_type(project_files)
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="app_builder_")
            
            # Write all files to temp directory
            for file_path, content in project_files.items():
                full_path = Path(temp_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
            
            # Determine command based on project type
            if project_type == "python":
                # Find entry point
                entry_point = next(
                    (path for path in project_files.keys() if "app.py" in path or "main.py" in path),
                    None
                )
                if entry_point:
                    cmd = ["python", entry_point]
                else:
                    return {
                        "success": False,
                        "output": "",
                        "errors": ["No Python entry point found"],
                        "exit_code": 1
                    }
            elif project_type == "node":
                # Install dependencies first (if package.json exists)
                if any("package.json" in path for path in project_files.keys()):
                    install_proc = await asyncio.create_subprocess_exec(
                        "npm", "install",
                        cwd=temp_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await install_proc.wait()
                
                cmd = ["node", "index.js"] if "index.js" in project_files else ["npm", "start"]
            else:
                return {
                    "success": False,
                    "output": f"Unsupported project type: {project_type}",
                    "errors": [f"Cannot execute {project_type} projects"],
                    "exit_code": 1
                }
            
            # Run the code with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=temp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30.0  # 30 second timeout
                )
                exit_code = process.returncode
                
                return {
                    "success": exit_code == 0,
                    "output": stdout.decode('utf-8', errors='ignore'),
                    "errors": stderr.decode('utf-8', errors='ignore').split('\n') if stderr else [],
                    "exit_code": exit_code
                }
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "output": "",
                    "errors": ["Execution timeout (30s)"],
                    "exit_code": -1
                }
                
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": [str(e)],
                "exit_code": 1
            }
        finally:
            # Clean up temporary directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def validate_app_runs(self, project_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate that the generated app runs without critical errors.
        
        Returns a dictionary with validation results.
        """
        # Check for entry point
        has_entry_point = any(
            "app.py" in path or "main.py" in path or "index.js" in path
            for path in project_files.keys()
        )
        
        if not has_entry_point:
            return {
                "valid": False,
                "error": "No entry point found. Expected app.py, main.py, or index.js",
                "errors": ["No entry point found"],
                "warnings": []
            }
        
        # TODO: Implement additional validation
        # - Check for syntax errors
        # - Verify dependencies are specified
        # - Run basic tests if applicable
        # - Check for common issues
        
        return {
            "valid": True,
            "errors": [],
            "warnings": ["Basic validation passed - entry point found"]
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

