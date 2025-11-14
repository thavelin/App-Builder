"""
Code Agent

Generates code and supporting files for the application.
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings


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

