"""
Usability Agent

Critiques UX and flow of the generated application.
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings


class UsabilityAgent:
    """
    Specialized agent for UX/Usability review.
    
    Responsibilities:
    - Critique user experience
    - Review user flow
    - Suggest improvements
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
    
    async def review_ux(self, code_result: Dict[str, Any], ui_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review the UX and flow of the generated application using OpenAI.
        
        Returns a dictionary with:
        - score: UX score (0-100)
        - issues: List of UX issues found
        - suggestions: List of improvement suggestions
        - flow_analysis: Analysis of user flow
        """
        print("    [UsabilityAgent] Starting UX review...", flush=True)
        if not self.client:
            print("    [UsabilityAgent] OpenAI not configured, using fallback", flush=True)
            # Fallback to placeholder if OpenAI is not configured
            return {
                "score": 75,
                "issues": ["OpenAI not configured for UX review"],
                "suggestions": ["Configure OpenAI API key for detailed UX analysis"],
                "flow_analysis": {
                    "user_journey": "Basic flow identified",
                    "pain_points": [],
                    "strengths": ["Basic structure present"]
                }
            }
        
        prompt = f"""You are a UX/Usability expert. Review the user experience of this application:

Code Structure: {json.dumps(code_result.get('structure', {}), indent=2)}
UI Design: {json.dumps(ui_result, indent=2)}

Please provide a JSON response with the following structure:
{{
    "score": 85,
    "issues": ["issue1", "issue2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "flow_analysis": {{
        "user_journey": "description of user journey",
        "pain_points": ["pain point 1", ...],
        "strengths": ["strength 1", ...]
    }}
}}

Requirements:
- Score should be 0-100 (higher is better)
- Identify specific UX issues
- Provide actionable improvement suggestions
- Analyze the user flow and journey
- Consider accessibility, usability, and user satisfaction

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a UX/Usability expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
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
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"OpenAI API error in UsabilityAgent: {e}")
            # Fallback response
            return {
                "score": 75,
                "issues": ["Error during UX review"],
                "suggestions": ["Review UX manually"],
                "flow_analysis": {
                    "user_journey": "Basic flow identified",
                    "pain_points": [],
                    "strengths": ["Basic structure present"]
                }
            }
    
    async def analyze_accessibility(self, ui_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze accessibility of the UI design.
        
        TODO: Implement accessibility analysis.
        """
        return {
            "score": 80,
            "issues": [],
            "recommendations": [
                "Ensure proper ARIA labels",
                "Check color contrast ratios"
            ]
        }

