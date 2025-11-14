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
        print(f"    [RequirementsAgent] Extracting spec from prompt...", flush=True)
        
        if not self.client:
            print("    [RequirementsAgent] OpenAI not configured, using fallback spec", flush=True)
            return self._fallback_spec(prompt)
        
        # Build context about attachments if provided
        attachment_context = ""
        if attachments:
            attachment_context = f"\n\nUser provided {len(attachments)} attachment(s):\n"
            for att in attachments:
                attachment_context += f"- {att.get('name')} ({att.get('type')})\n"
            attachment_context += "\nConsider these attachments when understanding requirements, but focus on the text prompt as primary source."
        
        system_prompt = """You are an expert software architect and requirements analyst. Your job is to extract structured requirements from natural language prompts.

You must:
1. Identify the core goal and purpose of the application
2. Determine who the target users are
3. Extract core features (high-level capabilities)
4. Identify data entities (things the app manages)
5. Define views/pages/screens needed
6. Note any technology preferences mentioned
7. Identify non-functional requirements (mobile-first, dark mode, etc.)
8. Note constraints (no database, static site, etc.)
9. Assess complexity level (tiny/small/medium/ambitious)
10. If the request is extremely ambitious, propose a realistic MVP scope

Be practical and reasonable. For vague prompts, infer sensible defaults. For overly ambitious requests, scope down to a solid MVP that covers the core end-to-end flow.

Always return valid JSON matching the AppSpec schema."""

        user_prompt = f"""Extract structured requirements from this user prompt:

{prompt}{attachment_context}

Return a JSON object with this exact structure:
{{
    "goal": "Short summary of what the user wants",
    "user_type": "Who the app is for",
    "core_features": ["feature1", "feature2", ...],
    "entities": [
        {{
            "name": "EntityName",
            "fields": [{{"name": "fieldName", "type": "string|number|boolean|date|etc"}}],
            "description": "What this entity represents"
        }}
    ],
    "views": [
        {{
            "name": "ViewName",
            "purpose": "What this view is for",
            "primary_actions": ["action1", "action2"],
            "description": "Additional details"
        }}
    ],
    "stack_preferences": ["technology1", "technology2"] or null,
    "non_functional_requirements": ["requirement1", "requirement2"],
    "constraints": ["constraint1", "constraint2"],
    "complexity_level": "tiny|small|medium|ambitious",
    "scope_notes": "Notes about scope adjustments if any, or null",
    "in_scope": ["explicitly in-scope feature1", "feature2"],
    "out_of_scope": ["explicitly out-of-scope feature1", "feature2"]
}}

Guidelines:
- If the prompt is vague, infer reasonable defaults (e.g., if no user type mentioned, use "general users")
- If the request is extremely ambitious (e.g., "build a full SaaS like Notion"), scope it down to a realistic MVP
- Always include at least one view (even if just "Home" or "Main")
- For CRUD apps, entities should match the data being managed
- Complexity: "tiny" = single page, "small" = few features, "medium" = multiple features, "ambitious" = complex (will be scoped down)
- Be explicit about what's in-scope vs out-of-scope

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent extraction
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
            
            spec_dict = json.loads(content)
            
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
            print(f"    [RequirementsAgent] ✓ Extracted spec: {spec.complexity_level.value} complexity, {len(spec.core_features)} features, {len(spec.views)} views", flush=True)
            return spec
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"    [RequirementsAgent] Error extracting spec: {e}, using fallback", flush=True)
            return self._fallback_spec(prompt)
    
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

