"""
UI Agent

Generates layout and wireframe suggestions for the application.
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings


class UIAgent:
    """
    Specialized agent for UI/UX design generation.
    
    Responsibilities:
    - Generate UI layouts and wireframes
    - Suggest component structures
    - Provide styling recommendations
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    async def generate_ui_design(self, description: str) -> Dict[str, Any]:
        """
        Generate UI design based on the task description using OpenAI.
        
        Returns a dictionary with:
        - layout: Layout structure
        - components: List of UI components
        - styling: Styling recommendations
        - wireframe: Wireframe description or data
        """
        print(f"    [UIAgent] Starting UI design generation for: {description[:60]}...", flush=True)
        if not self.client:
            print("    [UIAgent] OpenAI not configured, using fallback", flush=True)
            # Fallback to placeholder if OpenAI is not configured
            return {
                "layout": {
                    "type": "responsive",
                    "structure": "header, main, footer"
                },
                "components": [
                    {
                        "name": "Header",
                        "type": "navigation",
                        "description": "Main navigation header"
                    }
                ],
                "styling": {
                    "framework": "tailwind",
                    "theme": "modern",
                    "colors": "neutral"
                },
                "wireframe": "Basic wireframe structure"
            }
        
        prompt = f"""You are a UI/UX design expert. Design a user interface for this application:

{description}

Please provide a JSON response with the following structure:
{{
    "layout": {{
        "type": "responsive|mobile-first|desktop",
        "structure": "description of layout structure"
    }},
    "components": [
        {{
            "name": "ComponentName",
            "type": "navigation|form|display|container|etc",
            "description": "What this component does",
            "props": ["prop1", "prop2"]
        }},
        ...
    ],
    "styling": {{
        "framework": "tailwind|bootstrap|custom",
        "theme": "modern|classic|minimal",
        "colors": "color scheme description",
        "typography": "font recommendations"
    }},
    "wireframe": "Detailed wireframe description or structure"
}}

Requirements:
- Design a clean, modern, user-friendly interface
- Consider accessibility and usability
- Suggest appropriate UI components
- Provide styling recommendations
- Include a wireframe description

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a UI/UX design expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
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
            # Fallback response
            return {
                "layout": {"type": "responsive", "structure": "header, main, footer"},
                "components": [{"name": "Header", "type": "navigation", "description": "Main header"}],
                "styling": {"framework": "tailwind", "theme": "modern", "colors": "neutral"},
                "wireframe": "Basic layout structure"
            }
        except Exception as e:
            print(f"OpenAI API error in UIAgent: {e}")
            # Fallback response
            return {
                "layout": {"type": "responsive", "structure": "header, main, footer"},
                "components": [{"name": "Header", "type": "navigation", "description": "Main header"}],
                "styling": {"framework": "tailwind", "theme": "modern", "colors": "neutral"},
                "wireframe": "Basic layout structure"
            }
    
    async def generate_component_code(self, component_spec: Dict[str, Any]) -> str:
        """
        Generate actual component code (React, Vue, etc.) from component spec.
        
        TODO: Implement component code generation.
        """
        return f"// Generated component: {component_spec.get('name')}\n// TODO: Implement component generation"

