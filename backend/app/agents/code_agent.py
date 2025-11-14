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
    
    def _get_max_tokens(self) -> int:
        """Get appropriate max_tokens based on model completion token limits."""
        # Note: Completion tokens (max_tokens) are separate from context window size
        # Even models with large context windows (128k) typically limit completions to 4096 tokens
        
        # GPT-4 Turbo models (gpt-4-turbo-preview, gpt-4-1106-preview, gpt-4-turbo)
        if "turbo" in self.model.lower() or "1106" in self.model:
            return 4000  # Max completion tokens for turbo models (4096 limit, use 4000 for safety)
        # GPT-4o models
        elif "gpt-4o" in self.model.lower():
            return 4000  # Max completion tokens for GPT-4o (4096 limit, use 4000 for safety)
        # Standard gpt-4 has 8k context, completion limit is typically 4096 but be conservative
        elif "gpt-4" in self.model.lower():
            return 3500  # Conservative for standard gpt-4 (8k context)
        # GPT-3.5 models
        elif "gpt-3.5" in self.model.lower():
            return 2000  # Conservative for GPT-3.5
        # Default for other models
        else:
            return 2000  # Safe default
    
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
        import time
        start_time = time.time()
        print(f"    [CodeAgent] ===== Starting IMPLEMENTER phase =====", flush=True)
        print(f"    [CodeAgent] Generating code from AppSpec...", flush=True)
        print(f"    [CodeAgent] Model: {self.model}", flush=True)
        
        if not self.client:
            error_msg = "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            print(f"    [CodeAgent] ERROR: {error_msg}", flush=True)
            raise ValueError(error_msg)
        
        print(f"    [CodeAgent] OpenAI client initialized", flush=True)
        
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
        
        system_prompt = """You are an expert software developer (IMPLEMENTER phase). Your job is to generate complete, runnable code based on ARCHITECT_SPEC.

CRITICAL REQUIREMENTS:
1. Read and follow ARCHITECT_SPEC as the single source of truth
2. Generate COMPLETE, FUNCTIONAL code - no TODO comments for main features
3. Respect the stack and file list from ARCHITECT_SPEC
4. For "static_html" stack, generate a single index.html with inline CSS and JavaScript
5. Implement ALL features listed in ARCHITECT_SPEC.features
6. Follow the layout, persistence, and UX details exactly as specified
7. Use best practices and clean code
8. Ensure the app is directly runnable (e.g., save as index.html and open in browser)

The code must fully satisfy every requirement in ARCHITECT_SPEC."""

        # Get ARCHITECT_SPEC from app_spec if available
        architect_spec = getattr(app_spec, 'architect_spec', None) or app_spec.to_dict().get('architect_spec')

        if architect_spec:
            # Use ARCHITECT_SPEC directly (new workflow)
            user_prompt = f"""Generate a complete, runnable application based on this ARCHITECT_SPEC:

ARCHITECT_SPEC:
{json.dumps(architect_spec, indent=2)}
{iteration_context}

CRITICAL INSTRUCTIONS:
- Stack: {architect_spec.get('stack', 'static_html')}
- Files to generate: {', '.join(architect_spec.get('files', ['index.html']))}
- For static_html: Generate ONE file (index.html) with inline <style> and <script>
- Implement EVERY feature from the features list
- Follow the exact layout structure from requirements.layout
- Use the persistence method from requirements.persistence
- Implement all UX details exactly as specified
- Make it responsive as per requirements.responsiveness
- Apply styling as per requirements.style

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
- Implement ALL features from ARCHITECT_SPEC.features - no stubs or TODOs for main flows
- Follow ARCHITECT_SPEC exactly - layout, persistence, UX details
- Make it functional and well-structured
- For static_html, ensure index.html is complete and functional with inline CSS/JS

Return ONLY valid JSON, no markdown formatting or code blocks."""
        else:
            # Fallback to old format
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
            max_tokens = self._get_max_tokens()
            print(f"    [CodeAgent] Preparing API request: model={self.model}, max_tokens={max_tokens}", flush=True)
            if architect_spec:
                print(f"    [CodeAgent] Using ARCHITECT_SPEC workflow (stack: {architect_spec.get('stack', 'unknown')})", flush=True)
            else:
                print(f"    [CodeAgent] Using legacy AppSpec workflow", flush=True)
            
            api_start = time.time()
            print(f"    [CodeAgent] Calling OpenAI API...", flush=True)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            api_duration = time.time() - api_start
            print(f"    [CodeAgent] OpenAI API call completed in {api_duration:.2f}s", flush=True)
            print(f"    [CodeAgent] Response tokens: {response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 'unknown'}", flush=True)
            
            content = response.choices[0].message.content.strip()
            print(f"    [CodeAgent] Response length: {len(content)} characters", flush=True)
            
            # Remove markdown code blocks if present
            print(f"    [CodeAgent] Cleaning response (removing markdown if present)...", flush=True)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            print(f"    [CodeAgent] Parsing JSON response...", flush=True)
            result = json.loads(content)
            print(f"    [CodeAgent] JSON parsed successfully", flush=True)
            
            # Validate entry point exists
            files = result.get("files", [])
            entry_point = result.get("structure", {}).get("entry_point", "")
            print(f"    [CodeAgent] Generated {len(files)} files, entry point: {entry_point}", flush=True)
            if entry_point and not any(f.get("path") == entry_point for f in files):
                print(f"    [CodeAgent] WARNING: Entry point {entry_point} not found in generated files", flush=True)
            
            file_count = len(files)
            duration = time.time() - start_time
            print(f"    [CodeAgent] ✓ IMPLEMENTER phase complete in {duration:.2f}s", flush=True)
            print(f"    [CodeAgent] ✓ Generated {file_count} files", flush=True)
            print(f"    [CodeAgent] ===== IMPLEMENTER phase finished =====", flush=True)
            return result
            
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            error_msg = f"Failed to parse OpenAI response as JSON: {e}"
            print(f"    [CodeAgent] ERROR: JSON decode error after {duration:.2f}s: {error_msg}", flush=True)
            print(f"    [CodeAgent] Response content (first 500 chars): {content[:500] if 'content' in locals() else 'N/A'}", flush=True)
            raise ValueError(error_msg) from e
        except Exception as e:
            duration = time.time() - start_time
            error_str = str(e)
            import traceback
            print(f"    [CodeAgent] ERROR: Exception after {duration:.2f}s: {error_str}", flush=True)
            # Check for context length errors
            if "context_length_exceeded" in error_str.lower() or "maximum context length" in error_str.lower():
                error_msg = (
                    f"Context length exceeded. The prompt is too long for model {self.model}. "
                    f"Try: (1) Using a model with larger context (e.g., gpt-4-turbo-preview), "
                    f"(2) Simplifying your prompt, or (3) Reducing the scope of your app."
                )
                print(f"    [CodeAgent] ERROR: {error_msg}", flush=True)
                raise ValueError(error_msg) from e
            elif "api key" in error_str.lower() or "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                error_msg = "OpenAI API authentication failed. Please check your OPENAI_API_KEY."
                print(f"    [CodeAgent] ERROR: {error_msg}", flush=True)
                raise ValueError(error_msg) from e
            else:
                print(f"    [CodeAgent] Traceback:", flush=True)
                print(traceback.format_exc(), flush=True)
                error_msg = f"OpenAI API error: {error_str}"
                print(f"    [CodeAgent] ERROR: {error_msg}", flush=True)
                raise ValueError(error_msg) from e
    
    def _fallback_code(self, app_spec: "AppSpec") -> Dict[str, Any]:
        """
        Generate basic fallback code.
        NOTE: This should only be used in exceptional cases where we can't use OpenAI.
        """
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
        .error {{ color: #d32f2f; background: #ffebee; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{app_spec.goal}</h1>
    <div class="error">
        <strong>Error:</strong> Code generation failed. Please check the server logs for details.
        <br><br>
        Common issues:
        <ul>
            <li>OpenAI API key not configured (set OPENAI_API_KEY environment variable)</li>
            <li>Context length exceeded (try a simpler prompt or use gpt-4-turbo-preview model)</li>
            <li>API authentication error (check your API key is valid)</li>
        </ul>
    </div>
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
            max_tokens = self._get_max_tokens()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=max_tokens
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

