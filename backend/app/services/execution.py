"""
Execution Service

Handles sandbox/runner integration for validating generated code.
"""
import os
import zipfile
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path

# Entry point candidate filenames
ENTRYPOINT_CANDIDATES = ["app.py", "main.py", "index.js"]


def find_entrypoint(project_root: Path) -> Optional[Path]:
    """
    Recursively search for entry point files in the project directory.
    
    Args:
        project_root: Root directory of the project to search
        
    Returns:
        Path to the first entry point file found, or None if not found
    """
    for candidate in ENTRYPOINT_CANDIDATES:
        for path in project_root.rglob(candidate):
            return path
    return None


def find_entrypoint_in_file_paths(file_paths: List[str]) -> Optional[str]:
    """
    Find entry point by searching through file paths (for validation before extraction).
    
    Args:
        file_paths: List of file paths (as strings) to search
        
    Returns:
        First matching file path, or None if not found
    """
    for candidate in ENTRYPOINT_CANDIDATES:
        for file_path in file_paths:
            # Check if the path ends with the candidate filename
            if file_path.endswith(candidate) or f"/{candidate}" in file_path or f"\\{candidate}" in file_path:
                return file_path
    return None


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
        import json
        
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="app_builder_")
            project_root = Path(temp_dir)
            
            # Write all files to temp directory
            for file_path, content in project_files.items():
                full_path = project_root / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
            
            # Recursively find entry point
            entry_point_path = find_entrypoint(project_root)
            
            if not entry_point_path:
                # Log project structure for debugging
                root_items = [item.name for item in project_root.iterdir()][:10]
                print(f"Entry point not found in project root: {project_root}", flush=True)
                print(f"Top-level items: {root_items}", flush=True)
                
                return {
                    "success": False,
                    "output": "",
                    "errors": ["No entry point found. Expected app.py, main.py, or index.js"],
                    "exit_code": 1
                }
            
            # Log which entry point was found
            relative_entry_point = entry_point_path.relative_to(project_root)
            print(f"Using entry point: {relative_entry_point} (full path: {entry_point_path})", flush=True)
            
            # Determine command based on entry point file extension
            entry_point_suffix = entry_point_path.suffix
            
            if entry_point_suffix == ".py":
                # Python execution
                cmd = ["python", str(relative_entry_point)]
            elif entry_point_suffix == ".js":
                # Node/JavaScript execution
                # Install dependencies first (if package.json exists)
                package_json_path = project_root / "package.json"
                if package_json_path.exists():
                    install_proc = await asyncio.create_subprocess_exec(
                        "npm", "install",
                        cwd=temp_dir,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await install_proc.wait()
                    
                    # Check if package.json has a start script
                    try:
                        with open(package_json_path) as f:
                            package_data = json.load(f)
                            if "scripts" in package_data and "start" in package_data["scripts"]:
                                cmd = ["npm", "start"]
                            else:
                                cmd = ["node", str(relative_entry_point)]
                    except Exception as e:
                        print(f"Error reading package.json: {e}, using node directly", flush=True)
                        cmd = ["node", str(relative_entry_point)]
                else:
                    cmd = ["node", str(relative_entry_point)]
            else:
                return {
                    "success": False,
                    "output": "",
                    "errors": [f"Unsupported entry point file type: {entry_point_suffix}"],
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
        # Search for entry point recursively in file paths
        file_paths = list(project_files.keys())
        entry_point_path = find_entrypoint_in_file_paths(file_paths)
        
        if not entry_point_path:
            # Log project structure for debugging
            root_files = [path.split('/')[0].split('\\')[0] for path in file_paths[:20]]  # Top-level dirs/files
            root_files_unique = sorted(set(root_files))[:10]  # Limit to 10 unique entries
            
            print(f"Entry point validation failed. Project has {len(file_paths)} files.", flush=True)
            print(f"Top-level directories/files: {root_files_unique}", flush=True)
            
            return {
                "valid": False,
                "error": "No entry point found. Expected app.py, main.py, or index.js",
                "errors": ["No entry point found"],
                "warnings": []
            }
        
        print(f"Entry point found: {entry_point_path}", flush=True)
        
        # TODO: Implement additional validation
        # - Check for syntax errors
        # - Verify dependencies are specified
        # - Run basic tests if applicable
        # - Check for common issues
        
        return {
            "valid": True,
            "errors": [],
            "warnings": [f"Basic validation passed - entry point found: {entry_point_path}"]
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

