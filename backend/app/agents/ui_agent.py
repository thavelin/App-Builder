"""
UI Agent

Generates layout and wireframe suggestions for the application.
"""
import json
from typing import Dict, Any, List, TYPE_CHECKING
from openai import AsyncOpenAI
from app.config import settings

if TYPE_CHECKING:
    from app.schemas.app_spec import AppSpec


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
    
    async def generate_ux_plan(self, app_spec: "AppSpec") -> Dict[str, Any]:
        """
        Generate a structured UX plan from AppSpec.
        
        Input: AppSpec object
        Output: UX plan with views, layout sections, component lists, and navigation flow
        """
        import time
        start_time = time.time()
        print(f"    [UIAgent] ===== Starting UX plan generation =====", flush=True)
        print(f"    [UIAgent] Generating UX plan from AppSpec...", flush=True)
        
        # Check if architect_spec with ux_details exists - use it directly
        architect_spec = getattr(app_spec, 'architect_spec', None) or app_spec.to_dict().get('architect_spec')
        if architect_spec and architect_spec.get('ux_details'):
            print(f"    [UIAgent] Using ARCHITECT_SPEC.ux_details directly (no API call needed)", flush=True)
            ux_plan = self._convert_ux_details_to_plan(architect_spec['ux_details'], architect_spec)
            duration = time.time() - start_time
            print(f"    [UIAgent] ✓ UX plan generated from ARCHITECT_SPEC in {duration:.2f}s", flush=True)
            print(f"    [UIAgent] ✓ Generated UX plan with {len(ux_plan.get('views', []))} views", flush=True)
            print(f"    [UIAgent] ===== UX plan generation finished =====", flush=True)
            return ux_plan
        
        # If no OpenAI client, use fallback immediately
        if not self.client:
            print(f"    [UIAgent] OpenAI API key not configured, using fallback UX plan", flush=True)
            return self._fallback_ux_plan(app_spec)
        
        print(f"    [UIAgent] Model: {self.model}", flush=True)
        print(f"    [UIAgent] OpenAI client initialized", flush=True)
        
        system_prompt = """You are a UX/UI design expert. Your job is to create a concrete UX plan from an application specification.

You must provide:
1. For each view in the spec: layout sections, primary actions, and component lists
2. Navigation flow between views
3. Reusable component library

Focus on structure and flow, NOT pixel-perfect designs. Provide actionable guidance for implementation."""

        user_prompt = f"""Create a UX plan for this application specification:

{app_spec.summary()}

Views to design:
{json.dumps([{"name": v.name, "purpose": v.purpose, "primary_actions": v.primary_actions} for v in app_spec.views], indent=2)}

Entities:
{json.dumps([{"name": e.name, "fields": e.fields} for e in app_spec.entities], indent=2)}

Return a JSON object with this structure:
{{
    "views": [
        {{
            "name": "ViewName",
            "layout_sections": ["section1", "section2"],
            "components": ["Component1", "Component2"],
            "primary_actions": ["action1", "action2"],
            "description": "Layout description"
        }}
    ],
    "navigation_flow": {{
        "entry_point": "ViewName",
        "routes": [
            {{"from": "View1", "to": "View2", "trigger": "action/button"}}
        ]
    }},
    "component_library": [
        {{
            "name": "ComponentName",
            "type": "form|display|navigation|container",
            "description": "What it does",
            "used_in": ["View1", "View2"]
        }}
    ]
}}

Requirements:
- Design a concrete, implementable layout for each view
- Ensure navigation flow makes sense
- Identify reusable components
- Consider the app's purpose and user type
- Make it practical and buildable

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            print(f"    [UIAgent] Calling OpenAI API (model: {self.model}, max_tokens: 2000)...", flush=True)
            api_start = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            api_duration = time.time() - api_start
            print(f"    [UIAgent] OpenAI API call completed in {api_duration:.2f}s", flush=True)
            print(f"    [UIAgent] Response tokens: {response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 'unknown'}", flush=True)
            
            content = response.choices[0].message.content.strip()
            print(f"    [UIAgent] Response length: {len(content)} characters", flush=True)
            
            # Remove markdown code blocks if present
            print(f"    [UIAgent] Cleaning response (removing markdown if present)...", flush=True)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            print(f"    [UIAgent] Parsing JSON response...", flush=True)
            result = json.loads(content)
            duration = time.time() - start_time
            print(f"    [UIAgent] ✓ UX plan generation complete in {duration:.2f}s", flush=True)
            print(f"    [UIAgent] ✓ Generated UX plan with {len(result.get('views', []))} views", flush=True)
            print(f"    [UIAgent] ===== UX plan generation finished =====", flush=True)
            return result
            
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            print(f"    [UIAgent] ERROR: JSON decode error after {duration:.2f}s: {e}", flush=True)
            print(f"    [UIAgent] Response content (first 500 chars): {content[:500] if 'content' in locals() else 'N/A'}", flush=True)
            print(f"    [UIAgent] Using fallback UX plan", flush=True)
            return self._fallback_ux_plan(app_spec)
        except Exception as e:
            duration = time.time() - start_time
            import traceback
            print(f"    [UIAgent] ERROR: Exception after {duration:.2f}s: {e}", flush=True)
            print(f"    [UIAgent] Traceback:", flush=True)
            print(traceback.format_exc(), flush=True)
            print(f"    [UIAgent] Using fallback UX plan", flush=True)
            return self._fallback_ux_plan(app_spec)
    
    def _convert_ux_details_to_plan(self, ux_details: Dict[str, Any], architect_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ARCHITECT_SPEC.ux_details directly into a UX plan structure.
        This avoids unnecessary API calls when the spec already contains UX information.
        """
        views = []
        component_library = []
        all_components = set()
        
        # Convert ux_details structure to views
        for view_name, view_details in ux_details.items():
            if isinstance(view_details, list):
                # List format: ["item1", "item2", ...]
                components = []
                layout_sections = []
                primary_actions = []
                
                for item in view_details:
                    item_lower = item.lower()
                    if any(keyword in item_lower for keyword in ['button', 'click', 'action', 'submit', 'delete', 'save', 'edit', 'create', 'add']):
                        primary_actions.append(item)
                    elif any(keyword in item_lower for keyword in ['header', 'footer', 'sidebar', 'nav', 'main', 'panel', 'section']):
                        layout_sections.append(item)
                    else:
                        components.append(item)
                        all_components.add(item)
                
                # Default sections if none specified
                if not layout_sections:
                    if 'sidebar' in view_name.lower() or 'nav' in view_name.lower():
                        layout_sections = ['sidebar', 'main']
                    else:
                        layout_sections = ['header', 'main', 'footer']
                
                views.append({
                    "name": view_name.replace('_', ' ').title(),
                    "layout_sections": layout_sections,
                    "components": components if components else ["Content"],
                    "primary_actions": primary_actions,
                    "description": f"View for {view_name}"
                })
            elif isinstance(view_details, dict):
                # Dict format: {"sections": [...], "components": [...], ...}
                views.append({
                    "name": view_name.replace('_', ' ').title(),
                    "layout_sections": view_details.get("sections", ["header", "main", "footer"]),
                    "components": view_details.get("components", ["Content"]),
                    "primary_actions": view_details.get("actions", []),
                    "description": view_details.get("description", f"View for {view_name}")
                })
                all_components.update(view_details.get("components", []))
        
        # Build component library from collected components
        for comp in all_components:
            comp_lower = comp.lower()
            comp_type = "container"
            if any(kw in comp_lower for kw in ['button', 'link', 'nav']):
                comp_type = "navigation"
            elif any(kw in comp_lower for kw in ['form', 'input', 'field']):
                comp_type = "form"
            elif any(kw in comp_lower for kw in ['list', 'table', 'grid']):
                comp_type = "display"
            
            component_library.append({
                "name": comp,
                "type": comp_type,
                "description": f"Component for {comp}",
                "used_in": [v["name"] for v in views if comp in v.get("components", [])]
            })
        
        # Determine entry point from requirements.layout if available
        entry_point = views[0]["name"] if views else "Home"
        requirements = architect_spec.get('requirements', {})
        layout = requirements.get('layout', '')
        if 'sidebar' in layout.lower():
            # Find sidebar view
            sidebar_view = next((v for v in views if 'sidebar' in v["name"].lower() or 'nav' in v["name"].lower()), None)
            if sidebar_view:
                entry_point = sidebar_view["name"]
        
        return {
            "views": views,
            "navigation_flow": {
                "entry_point": entry_point,
                "routes": []
            },
            "component_library": component_library if component_library else [
                {"name": "Content", "type": "container", "description": "Main content area", "used_in": [v["name"] for v in views]}
            ]
        }
    
    def _fallback_ux_plan(self, app_spec: "AppSpec") -> Dict[str, Any]:
        """
        Generate a fallback UX plan.
        First tries to use architect_spec.ux_details if available, otherwise uses AppSpec.views.
        """
        # Try to use architect_spec.ux_details first
        architect_spec = getattr(app_spec, 'architect_spec', None) or app_spec.to_dict().get('architect_spec')
        if architect_spec and architect_spec.get('ux_details'):
            print(f"    [UIAgent] Using ARCHITECT_SPEC.ux_details for fallback plan", flush=True)
            return self._convert_ux_details_to_plan(architect_spec['ux_details'], architect_spec)
        
        # Fallback to AppSpec.views if available
        views = []
        if hasattr(app_spec, 'views') and app_spec.views:
            for view in app_spec.views:
                views.append({
                    "name": view.name,
                    "layout_sections": ["header", "main", "footer"],
                    "components": ["Navigation", "Content"],
                    "primary_actions": view.primary_actions if hasattr(view, 'primary_actions') else [],
                    "description": view.purpose if hasattr(view, 'purpose') else f"View: {view.name}"
                })
        else:
            # Ultimate fallback: create a single view
            views = [{
                "name": "Main",
                "layout_sections": ["header", "main", "footer"],
                "components": ["Content"],
                "primary_actions": [],
                "description": "Main application view"
            }]
        
        return {
            "views": views,
            "navigation_flow": {
                "entry_point": views[0]["name"] if views else "Home",
                "routes": []
            },
            "component_library": [
                {"name": "Navigation", "type": "navigation", "description": "Main navigation", "used_in": [v["name"] for v in views]},
                {"name": "Content", "type": "container", "description": "Main content area", "used_in": [v["name"] for v in views]}
            ]
        }
    
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

