"""
Requirements / Architect Agent

Extracts structured AppSpec from natural language user prompts.
Handles complexity assessment and scope adjustment.
"""
import json
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from app.config import settings
from app.schemas.app_spec import AppSpec, ComplexityLevel, Entity, View


class RequirementsAgent:
    """
    Specialized agent for extracting structured requirements from user prompts.
    
    Responsibilities:
    - Parse natural language prompts into structured AppSpec
    - Assess complexity and scope appropriately
    - Infer reasonable defaults when user is vague
    - Propose MVP scope for ambitious requests
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    async def extract_spec(
        self,
        prompt: str,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> AppSpec:
        """
        Extract structured AppSpec from a natural language prompt.
        
        Args:
            prompt: User's natural language description
            attachments: Optional file attachments (images, documents)
        
        Returns:
            AppSpec object representing the structured requirements
        """
        import time
        start_time = time.time()
        print(f"    [RequirementsAgent] ===== Starting ARCHITECT phase =====", flush=True)
        print(f"    [RequirementsAgent] Extracting spec from prompt...", flush=True)
        print(f"    [RequirementsAgent] Prompt length: {len(prompt)} characters", flush=True)
        print(f"    [RequirementsAgent] Model: {self.model}", flush=True)
        
        if not self.client:
            print("    [RequirementsAgent] ERROR: OpenAI not configured, using fallback spec", flush=True)
            return self._fallback_spec(prompt)
        
        print(f"    [RequirementsAgent] OpenAI client initialized, preparing API request...", flush=True)
        
        # Build context about attachments if provided
        attachment_context = ""
        image_attachments = []
        if attachments:
            attachment_context = f"\n\nUser provided {len(attachments)} attachment(s):\n"
            for att in attachments:
                # Handle both Pydantic models and dicts
                # Check if it's a Pydantic model by checking for model_dump method or name attribute
                if hasattr(att, 'model_dump') or (hasattr(att, 'name') and not isinstance(att, dict)):
                    # Pydantic model - use attribute access
                    try:
                        att_name = att.name
                        att_type = att.type
                        att_content = att.content
                    except AttributeError:
                        # Fallback: try to convert to dict
                        if hasattr(att, 'model_dump'):
                            att_dict = att.model_dump()
                            att_name = att_dict.get('name', 'unknown')
                            att_type = att_dict.get('type', 'unknown')
                            att_content = att_dict.get('content', '')
                        else:
                            att_name = 'unknown'
                            att_type = 'unknown'
                            att_content = ''
                elif isinstance(att, dict):
                    # Dictionary - use .get()
                    att_name = att.get('name', 'unknown')
                    att_type = att.get('type', 'unknown')
                    att_content = att.get('content', '')
                else:
                    # Unknown type - try attribute access first, then dict access
                    try:
                        att_name = getattr(att, 'name', 'unknown')
                        att_type = getattr(att, 'type', 'unknown')
                        att_content = getattr(att, 'content', '')
                    except:
                        att_name = 'unknown'
                        att_type = 'unknown'
                        att_content = ''
                
                attachment_context += f"- {att_name} ({att_type})\n"
                
                # Check if it's an image attachment
                if att_type and att_type.startswith('image/') and att_content:
                    # Determine data URL format based on content
                    if att_content.startswith('data:'):
                        # Already a data URL
                        image_url = att_content
                    else:
                        # Base64 content, create data URL
                        image_url = f"data:{att_type};base64,{att_content}"
                    
                    image_attachments.append({
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    })
                    print(f"    [RequirementsAgent] Added image attachment: {att_name} ({att_type})", flush=True)
            
            if not image_attachments:
                attachment_context += "\nConsider these attachments when understanding requirements, but focus on the text prompt as primary source."
            else:
                attachment_context += f"\nThe user has provided {len(image_attachments)} image(s). Please analyze the image(s) carefully when understanding the requirements."
        
        system_prompt = """You are an expert software architect (ARCHITECT phase). Your job is to expand the user's APP_BRIEF into a detailed ARCHITECT_SPEC JSON.

You must produce a concrete, structured spec that includes:
1. Stack choice (default to "static_html" for simple one-page apps unless clearly specified otherwise)
2. File list (e.g. ["index.html"] for static HTML apps)
3. Requirements (persistence method, layout structure, responsiveness, styling constraints)
4. Data model (entities with fields and types)
5. Features (explicit user stories like "create a new note", "edit note title/body", etc.)
6. UX details (structured breakdown of each view: navigation, components, empty states, actions)

Be concrete and opinionated. Infer sensible defaults if the user is vague. Scope down overly ambitious requests to a realistic MVP.

Output the spec between ARCHITECT_SPEC_START and ARCHITECT_SPEC_END markers."""

        user_prompt = f"""Expand this APP_BRIEF into a detailed ARCHITECT_SPEC:

APP_BRIEF:
{prompt}{attachment_context}

Output ARCHITECT_SPEC_START followed by a JSON object with this exact structure:

IMPORTANT: You MUST output the JSON between ARCHITECT_SPEC_START and ARCHITECT_SPEC_END markers.
{{
    "stack": "static_html",
    "files": ["index.html"],
    "requirements": {{
        "persistence": "localStorage",
        "layout": "sidebar (notes list) + main panel (selected note)",
        "responsiveness": "works well from 375px width up to desktop",
        "style": "minimal, clean, light theme, system font"
    }},
    "data_model": {{
        "note": {{
            "id": "string",
            "title": "string",
            "body": "string",
            "updatedAt": "number (timestamp)"
        }}
    }},
    "features": [
        "Create a new note",
        "Edit note title and body",
        "Delete a note with confirmation",
        "Highlight selected note in sidebar",
        "Sort notes by last updated descending",
        "Show an empty state when there are no notes",
        "Persist notes in localStorage"
    ],
    "ux_details": {{
        "sidebar": [
            "List of notes with title and last-updated date",
            "Clicking a note selects it"
        ],
        "main_panel": [
            "Editable title input",
            "Large textarea for body",
            "Delete button",
            "Empty state message if no notes"
        ]
    }}
}}

Guidelines:
- Choose "static_html" for simple apps unless the brief clearly asks for a framework
- Be concrete about layout (e.g., "sidebar + main panel", "single column", "grid layout")
- Specify persistence method (localStorage, IndexedDB, or "none" for stateless apps)
- List ALL features as explicit user stories
- Break down UX details by view/component with specific elements
- Infer sensible defaults if the user is vague
- Scope down ambitious requests to a realistic MVP

End with ARCHITECT_SPEC_END. Return ONLY the JSON between the markers, no markdown code blocks."""

        try:
            # Build user message content - include images if present
            user_message_content = [{"type": "text", "text": user_prompt}]
            if image_attachments:
                user_message_content.extend(image_attachments)
                # Use vision-capable model if images are present
                # Check if current model supports vision
                if "gpt-4o" in self.model.lower() or "vision" in self.model.lower() or "gpt-4-turbo" in self.model.lower():
                    # Model already supports vision
                    actual_model = self.model
                else:
                    # Switch to a vision-capable model
                    actual_model = "gpt-4o"  # gpt-4o has built-in vision support
                    print(f"    [RequirementsAgent] Images detected, switching from {self.model} to {actual_model} for vision support.", flush=True)
            else:
                actual_model = self.model
            
            print(f"    [RequirementsAgent] Calling OpenAI API (model: {actual_model}, max_tokens: 2000, images: {len(image_attachments)})...", flush=True)
            api_start = time.time()
            response = await self.client.chat.completions.create(
                model=actual_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message_content if image_attachments else user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=2000
            )
            api_duration = time.time() - api_start
            print(f"    [RequirementsAgent] OpenAI API call completed in {api_duration:.2f}s", flush=True)
            print(f"    [RequirementsAgent] Response tokens: {response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 'unknown'}", flush=True)
            
            content = response.choices[0].message.content.strip()
            print(f"    [RequirementsAgent] Response length: {len(content)} characters", flush=True)
            
            # Extract ARCHITECT_SPEC from between markers
            start_marker = "ARCHITECT_SPEC_START"
            end_marker = "ARCHITECT_SPEC_END"
            
            print(f"    [RequirementsAgent] Looking for markers: {start_marker} and {end_marker}", flush=True)
            if start_marker in content and end_marker in content:
                print(f"    [RequirementsAgent] Found both markers, extracting JSON...", flush=True)
                start_idx = content.find(start_marker) + len(start_marker)
                end_idx = content.find(end_marker)
                content = content[start_idx:end_idx].strip()
            else:
                print(f"    [RequirementsAgent] WARNING: Markers not found, attempting to parse directly...", flush=True)
                # Fallback: remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
            
            print(f"    [RequirementsAgent] Parsing JSON (length: {len(content)} chars)...", flush=True)
            architect_spec = json.loads(content)
            print(f"    [RequirementsAgent] JSON parsed successfully", flush=True)
            
            # Store the raw ARCHITECT_SPEC in the spec for the Code Agent to use
            # Convert ARCHITECT_SPEC to AppSpec format for backward compatibility
            spec_dict = self._convert_architect_spec_to_app_spec(architect_spec, prompt)
            
            # Store raw ARCHITECT_SPEC as metadata
            spec_dict["architect_spec"] = architect_spec
            
            # Convert complexity_level string to enum
            if isinstance(spec_dict.get("complexity_level"), str):
                try:
                    spec_dict["complexity_level"] = ComplexityLevel(spec_dict["complexity_level"].lower())
                except ValueError:
                    spec_dict["complexity_level"] = ComplexityLevel.SMALL
            
            # Handle scope adjustment for ambitious requests
            if spec_dict.get("complexity_level") == ComplexityLevel.AMBITIOUS:
                print(f"    [RequirementsAgent] Request is ambitious, ensuring MVP scope is defined", flush=True)
                if not spec_dict.get("scope_notes"):
                    spec_dict["scope_notes"] = "Original request was ambitious; scoped down to a focused MVP covering core functionality."
            
            # Ensure we have at least basic structure
            if not spec_dict.get("views"):
                spec_dict["views"] = [{"name": "Home", "purpose": "Main application view", "primary_actions": []}]
            
            if not spec_dict.get("core_features"):
                spec_dict["core_features"] = ["Basic functionality"]
            
            spec = AppSpec(**spec_dict)
            duration = time.time() - start_time
            print(f"    [RequirementsAgent] ✓ ARCHITECT phase complete in {duration:.2f}s", flush=True)
            print(f"    [RequirementsAgent] ✓ Extracted ARCHITECT_SPEC: {architect_spec.get('stack', 'unknown')} stack, {len(architect_spec.get('features', []))} features", flush=True)
            print(f"    [RequirementsAgent] ===== ARCHITECT phase finished =====", flush=True)
            return spec

        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            print(f"    [RequirementsAgent] ERROR: JSON decode error after {duration:.2f}s: {e}", flush=True)
            print(f"    [RequirementsAgent] Response content (first 500 chars): {content[:500] if 'content' in locals() else 'N/A'}", flush=True)
            print(f"    [RequirementsAgent] Using fallback spec", flush=True)
            return self._fallback_spec(prompt)
        except Exception as e:
            duration = time.time() - start_time
            import traceback
            print(f"    [RequirementsAgent] ERROR: Exception after {duration:.2f}s: {e}", flush=True)
            print(f"    [RequirementsAgent] Traceback:", flush=True)
            print(traceback.format_exc(), flush=True)
            print(f"    [RequirementsAgent] Using fallback spec", flush=True)
            return self._fallback_spec(prompt)
    
    def _convert_architect_spec_to_app_spec(self, architect_spec: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Convert ARCHITECT_SPEC format to AppSpec format."""
        # Extract data model entities
        entities = []
        data_model = architect_spec.get("data_model", {})
        for entity_name, fields in data_model.items():
            entity_fields = []
            if isinstance(fields, dict):
                for field_name, field_type in fields.items():
                    entity_fields.append({
                        "name": field_name,
                        "type": str(field_type) if not isinstance(field_type, str) else field_type
                    })
            entities.append({
                "name": entity_name,
                "fields": entity_fields,
                "description": f"Entity representing {entity_name}"
            })
        
        # Extract views from ux_details
        views = []
        ux_details = architect_spec.get("ux_details", {})
        for view_name, view_components in ux_details.items():
            primary_actions = []
            if isinstance(view_components, list):
                # Extract actions from component descriptions
                for comp in view_components:
                    if isinstance(comp, str) and any(action in comp.lower() for action in ["button", "click", "action", "delete", "edit", "create", "save"]):
                        primary_actions.append(comp)
            
            views.append({
                "name": view_name.replace("_", " ").title(),
                "purpose": f"View for {view_name}",
                "primary_actions": primary_actions[:3],  # Limit to 3
                "description": "; ".join(view_components) if isinstance(view_components, list) else str(view_components)
            })
        
        # If no views extracted, create a default one
        if not views:
            views = [{"name": "Home", "purpose": "Main application view", "primary_actions": [], "description": ""}]
        
        # Determine complexity based on features count
        features = architect_spec.get("features", [])
        if len(features) <= 3:
            complexity = "tiny"
        elif len(features) <= 6:
            complexity = "small"
        elif len(features) <= 10:
            complexity = "medium"
        else:
            complexity = "ambitious"
        
        # Extract stack preferences
        stack = architect_spec.get("stack", "static_html")
        stack_preferences = [stack] if stack != "static_html" else None
        
        # Extract constraints from requirements
        requirements = architect_spec.get("requirements", {})
        constraints = []
        if requirements.get("persistence") == "none":
            constraints.append("No persistence")
        if stack == "static_html":
            constraints.append("Static site only")
        
        return {
            "goal": prompt[:200] if len(prompt) > 200 else prompt,
            "user_type": "general users",
            "core_features": features,
            "entities": entities,
            "views": views,
            "stack_preferences": stack_preferences,
            "non_functional_requirements": [
                requirements.get("responsiveness", ""),
                requirements.get("style", "")
            ] if requirements else [],
            "constraints": constraints,
            "complexity_level": complexity,
            "scope_notes": None,
            "in_scope": features,
            "out_of_scope": []
        }
    
    def _fallback_spec(self, prompt: str) -> AppSpec:
        """Generate a basic fallback spec when OpenAI is not available."""
        return AppSpec(
            goal=prompt[:200],
            user_type="general users",
            core_features=["Basic functionality"],
            entities=[],
            views=[View(name="Home", purpose="Main application view", primary_actions=[])],
            complexity_level=ComplexityLevel.SMALL,
            scope_notes="Fallback spec generated (OpenAI not configured)"
        )

