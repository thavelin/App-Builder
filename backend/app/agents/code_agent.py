"""
Code Agent

Generates code and supporting files for the application.
"""
import json
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from openai import AsyncOpenAI
from app.config import settings

if TYPE_CHECKING:
    from app.schemas.app_spec import AppSpec


class CodeAgent:
    """
    Specialized agent for generating application code.
    
    Responsibilities:
    - Generate code files based on requirements
    - Create supporting files (config, dependencies, etc.)
    - Structure the project appropriately
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    async def generate_code_from_spec(
        self,
        app_spec: "AppSpec",
        ux_plan: Dict[str, Any],
        previous_code: Optional[Dict[str, Any]] = None,
        repair_brief: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code based on AppSpec and UX plan.
        
        Args:
            app_spec: Structured application specification
            ux_plan: UX plan with views, components, and navigation
            previous_code: Optional previous code for iterations
            repair_brief: Optional brief describing what needs to be fixed
        
        Returns:
            Dictionary with files, structure, and dependencies
        """
        print(f"    [CodeAgent] Generating code from AppSpec...", flush=True)
        if not self.client:
            print("    [CodeAgent] OpenAI not configured, using fallback", flush=True)
            return self._fallback_code(app_spec)
        
        iteration_context = ""
        if previous_code and repair_brief:
            iteration_context = f"""

PREVIOUS ITERATION CODE:
{json.dumps(previous_code.get('structure', {}), indent=2)}

REPAIR BRIEF (what needs to be fixed):
{repair_brief}

You should:
- Keep working code from the previous iteration
- Fix the issues mentioned in the repair brief
- Ensure the code is complete and functional
- Do NOT leave TODO comments for main user flows
"""
        
        system_prompt = """You are an expert software developer. Your job is to generate complete, runnable code based on an application specification and UX plan.

CRITICAL REQUIREMENTS:
1. Generate COMPLETE, FUNCTIONAL code - no TODO comments for main features
2. Always include a root-level entry point (app.py, main.py, index.js, or index.html)
3. Respect stack preferences when possible, otherwise use sensible defaults
4. Implement ALL core features from the spec
5. Create a working MVP that covers the core end-to-end flow
6. Use best practices and clean code
7. Add helpful comments
8. Ensure the project structure is clear and runnable

For static sites, use index.html as entry point. For backend apps, use app.py or main.py."""

        user_prompt = f"""Generate a complete, runnable application based on this specification:

APP SPECIFICATION:
{app_spec.summary()}

Core Features: {', '.join(app_spec.core_features)}
Stack Preferences: {app_spec.stack_preferences or 'None specified - use sensible defaults'}
Non-functional Requirements: {', '.join(app_spec.non_functional_requirements) if app_spec.non_functional_requirements else 'None'}
Constraints: {', '.join(app_spec.constraints) if app_spec.constraints else 'None'}

UX PLAN:
{json.dumps(ux_plan, indent=2)}

ENTITIES:
{json.dumps([{"name": e.name, "fields": e.fields} for e in app_spec.entities], indent=2)}
{iteration_context}

Return a JSON object with this structure:
{{
    "files": [
        {{"path": "filename.ext", "content": "complete file content here"}},
        ...
    ],
    "structure": {{
        "type": "python|node|react|html|etc",
        "entry_point": "main file path (app.py, main.py, index.js, or index.html)"
    }},
    "dependencies": ["package1", "package2", ...]
}}

Requirements:
- Generate ALL necessary files for a complete, runnable project
- Include entry point at project root (app.py, main.py, index.js, or index.html)
- Implement ALL core features - no stubs or TODOs for main flows
- Include configuration files, dependency files, README if helpful
- Use the UX plan to structure the UI
- Respect stack preferences or use sensible defaults
- Make it functional and well-structured
- For static sites, ensure index.html is complete and functional
- For backend apps, ensure proper entry points and structure

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=8000  # Increased for complete code generation
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Validate entry point exists
            files = result.get("files", [])
            entry_point = result.get("structure", {}).get("entry_point", "")
            if entry_point and not any(f.get("path") == entry_point for f in files):
                print(f"    [CodeAgent] Warning: Entry point {entry_point} not found in generated files", flush=True)
            
            file_count = len(files)
            print(f"    [CodeAgent] ✓ Generated {file_count} files", flush=True)
            return result
            
        except json.JSONDecodeError as e:
            print(f"    [CodeAgent] Failed to parse response: {e}, using fallback", flush=True)
            return self._fallback_code(app_spec)
        except Exception as e:
            print(f"    [CodeAgent] Error: {e}, using fallback", flush=True)
            return self._fallback_code(app_spec)
    
    def _fallback_code(self, app_spec: "AppSpec") -> Dict[str, Any]:
        """Generate basic fallback code."""
        return {
            "files": [
                {
                    "path": "index.html",
                    "content": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_spec.goal}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>{app_spec.goal}</h1>
    <p>Generated application - OpenAI not configured</p>
</body>
</html>"""
                }
            ],
            "structure": {"type": "html", "entry_point": "index.html"},
            "dependencies": []
        }
    
    async def generate_code(self, description: str) -> Dict[str, Any]:
        """
        Generate code based on the task description using OpenAI.
        
        The generated project must include a root-level entry point file (app.py, main.py, index.js, or index.html)
        that can be used to run the application. This entry point is required for validation and execution.
        For static sites, index.html is a valid entry point.
        
        Returns a dictionary with:
        - files: List of file paths and their contents
        - structure: Project structure information
        - dependencies: Required dependencies
        """
        print(f"    [CodeAgent] Starting code generation for: {description[:60]}...", flush=True)
        if not self.client:
            print("    [CodeAgent] OpenAI not configured, using fallback", flush=True)
            # Fallback to placeholder if OpenAI is not configured
            # Include both app.py and root-level main.py for proper entrypoint
            return {
                "files": [
                    {
                        "path": "app.py",
                        "content": f"""# Generated code for: {description}
# OpenAI API key not configured

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Hello, World!"}}
"""
                    },
                    {
                        "path": "main.py",
                        "content": """# Entry point at project root
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
                    },
                    {
                        "path": "requirements.txt",
                        "content": "# Dependencies\nfastapi\nuvicorn"
                    }
                ],
                "structure": {
                    "type": "python",
                    "entry_point": "main.py"
                },
                "dependencies": ["fastapi", "uvicorn"]
            }
        
        prompt = f"""You are an expert software developer. Generate a complete, working application based on this description:

{description}

Please provide a JSON response with the following structure:
{{
    "files": [
        {{"path": "filename.py", "content": "file content here"}},
        ...
    ],
    "structure": {{
        "type": "python|node|react|etc",
        "entry_point": "main file path"
    }},
    "dependencies": ["package1", "package2", ...]
}}

Requirements:
- Generate complete, runnable code
- Include all necessary files (main code, config files, dependencies file)
- Use best practices and clean code
- Add helpful comments
- Ensure the code is functional and well-structured
- The root of the project must contain a file named app.py, main.py, index.js, or index.html which acts as the entry point for running the app. Use index.html for static websites.

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            # Fallback response with root-level entrypoint
            return {
                "files": [
                    {
                        "path": "app.py",
                        "content": f"""# Generated code for: {description}
# Error parsing AI response

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Hello, World!"}}
"""
                    },
                    {
                        "path": "main.py",
                        "content": """# Entry point at project root
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
                    }
                ],
                "structure": {"type": "python", "entry_point": "main.py"},
                "dependencies": ["fastapi", "uvicorn"]
            }
        except Exception as e:
            print(f"OpenAI API error in CodeAgent: {e}")
            # Fallback response with root-level entrypoint
            return {
                "files": [
                    {
                        "path": "app.py",
                        "content": f"""# Generated code for: {description}
# OpenAI API error occurred

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Hello, World!"}}
"""
                    },
                    {
                        "path": "main.py",
                        "content": """# Entry point at project root
from app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
                    }
                ],
                "structure": {"type": "python", "entry_point": "main.py"},
                "dependencies": ["fastapi", "uvicorn"]
            }
    
    async def generate_supporting_files(self, project_type: str) -> List[Dict[str, str]]:
        """
        Generate supporting files like README, .gitignore, etc.
        
        TODO: Implement based on project type.
        """
        return [
            {
                "path": "README.md",
                "content": "# Generated Application\n\nThis app was generated by AI App Builder."
            },
            {
                "path": ".gitignore",
                "content": "__pycache__/\n*.pyc\n.env\n"
            }
        ]

