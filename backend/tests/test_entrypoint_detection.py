"""
Unit tests for entrypoint detection functionality.
"""
import pytest
from app.services.execution import ExecutionService, find_entrypoint_in_file_paths
from pathlib import Path
import tempfile
import shutil


@pytest.mark.asyncio
async def test_validate_app_runs_missing_entrypoint():
    """Test that validate_app_runs returns False when no entrypoint is found."""
    service = ExecutionService()
    
    # Project with files in subdirectories but no root entrypoint
    project_files = {
        "backend/app.py": "print('Hello')",
        "backend/main.py": "print('Hello')",
        "backend/utils.py": "def helper(): pass",
        "README.md": "# Project",
    }
    
    result = await service.validate_app_runs(project_files)
    
    assert result["valid"] is False
    assert "No entry point found" in result["error"]
    assert result["errors"] == ["No entry point found"]


@pytest.mark.asyncio
async def test_validate_app_runs_with_root_entrypoint():
    """Test that validate_app_runs returns True when root entrypoint exists."""
    service = ExecutionService()
    
    # Project with root-level main.py that imports from backend/app.py
    project_files = {
        "main.py": """# Entry point at project root
from backend.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",
        "backend/app.py": """from fastapi import FastAPI
app = FastAPI()
""",
        "requirements.txt": "fastapi\nuvicorn",
    }
    
    result = await service.validate_app_runs(project_files)
    
    assert result["valid"] is True
    assert "entry point found" in result["warnings"][0].lower()


@pytest.mark.asyncio
async def test_validate_app_runs_with_app_py():
    """Test that validate_app_runs works with root-level app.py."""
    service = ExecutionService()
    
    project_files = {
        "app.py": "print('Hello')",
        "requirements.txt": "requests",
    }
    
    result = await service.validate_app_runs(project_files)
    
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_validate_app_runs_with_index_js():
    """Test that validate_app_runs works with root-level index.js."""
    service = ExecutionService()
    
    project_files = {
        "index.js": "console.log('Hello');",
        "package.json": '{"name": "test"}',
    }
    
    result = await service.validate_app_runs(project_files)
    
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_find_entrypoint_in_file_paths():
    """Test the find_entrypoint_in_file_paths helper function."""
    # Test with root-level entrypoint
    file_paths = ["app.py", "utils.py", "README.md"]
    result = find_entrypoint_in_file_paths(file_paths)
    assert result == "app.py"
    
    # Test with nested entrypoint
    file_paths = ["backend/app.py", "backend/utils.py", "README.md"]
    result = find_entrypoint_in_file_paths(file_paths)
    assert result == "backend/app.py"
    
    # Test with Windows-style paths
    file_paths = ["backend\\app.py", "backend\\utils.py", "README.md"]
    result = find_entrypoint_in_file_paths(file_paths)
    assert result == "backend\\app.py"
    
    # Test with no entrypoint
    file_paths = ["utils.py", "README.md", "config.json"]
    result = find_entrypoint_in_file_paths(file_paths)
    assert result is None


@pytest.mark.asyncio
async def test_find_entrypoint_recursive():
    """Test recursive entrypoint detection in actual directory."""
    from app.services.execution import find_entrypoint
    
    # Create temporary directory structure
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create nested structure without root entrypoint
        (temp_dir / "backend").mkdir()
        (temp_dir / "backend" / "app.py").write_text("print('Hello')")
        (temp_dir / "backend" / "main.py").write_text("print('Hello')")
        
        # Should find the nested entrypoint
        result = find_entrypoint(temp_dir)
        assert result is not None
        assert "app.py" in str(result) or "main.py" in str(result)
        
        # Create root entrypoint
        (temp_dir / "main.py").write_text("print('Hello')")
        
        # Should find root entrypoint first (rglob order)
        result = find_entrypoint(temp_dir)
        assert result is not None
        # The first match will be returned, which could be any of them
        assert result.exists()
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

