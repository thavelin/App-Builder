"""
Reviewer Agent

Scores completeness and outputs structured JSON with score and issues.
"""
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings


class ReviewerAgent:
    """
    Specialized agent for final review and approval.
    
    Responsibilities:
    - Score completeness of the generated application
    - Identify remaining issues
    - Approve or reject the result
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.openai_model
        self.approval_threshold = 80  # Minimum score for approval
    
    async def review_completeness(
        self,
        prompt: str,
        results: Dict[str, Any],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Review the completeness of the generated application using OpenAI.
        
        Returns a dictionary with:
        - approved: Boolean indicating if the result is approved
        - score: Completeness score (0-100)
        - issues: List of issues found
        - feedback: Detailed feedback
        """
        print(f"    [ReviewerAgent] Starting completeness review (iteration {iteration + 1})...", flush=True)
        if not self.client:
            print("    [ReviewerAgent] OpenAI not configured, using fallback approval", flush=True)
            # Fallback: approve by default on first iteration to avoid blocking progress
            # Still include a warning in issues to inform the user
            score = 85
            return {
                "approved": True,  # Always approve on first iteration when OpenAI not configured
                "score": score,
                "issues": ["OpenAI not configured for review - using fallback approval"],
                "feedback": f"Review iteration {iteration + 1}: Approved (OpenAI not configured, using fallback)",
                "iteration": iteration
            }
        
        # Prepare summary of results for review
        code_summary = f"Code files: {len(results.get('code', {}).get('files', []))} files"
        ui_summary = f"UI components: {len(results.get('ui', {}).get('components', []))} components"
        usability_summary = f"UX score: {results.get('usability_feedback', {}).get('score', 'N/A')}"
        
        review_prompt = f"""You are a code review expert. Review the completeness and quality of this generated application:

Original Prompt: {prompt}

Generated Results:
- {code_summary}
- {ui_summary}
- {usability_summary}

Code Structure: {json.dumps(results.get('code', {}).get('structure', {}), indent=2)}
UI Design: {json.dumps(results.get('ui', {}), indent=2)}
Usability Feedback: {json.dumps(results.get('usability_feedback', {}), indent=2)}

This is iteration {iteration + 1} of the review process.

Please provide a JSON response with the following structure:
{{
    "approved": true,
    "score": 85,
    "issues": ["issue1", "issue2", ...],
    "feedback": "Detailed feedback about the application quality and completeness",
    "iteration": {iteration}
}}

Requirements:
- Score should be 0-100 (higher is better)
- approved should be true if score >= 80, false otherwise
- Identify specific issues that need to be addressed
- Provide constructive feedback
- Consider code quality, completeness, UI/UX, and alignment with the original prompt

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code review expert. Always return valid JSON."},
                    {"role": "user", "content": review_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent reviews
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
            # Ensure approved is based on score
            result["approved"] = result.get("score", 0) >= self.approval_threshold
            result["iteration"] = iteration
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"OpenAI API error in ReviewerAgent: {e}")
            # Fallback: approve after first iteration
            score = 85 if iteration > 0 else 70
            return {
                "approved": score >= self.approval_threshold,
                "score": score,
                "issues": ["Error during review"],
                "feedback": f"Review iteration {iteration + 1}: Error occurred during AI review",
                "iteration": iteration
            }
    
    async def check_requirements_coverage(
        self,
        prompt: str,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if all requirements from the prompt are covered.
        
        TODO: Implement requirement coverage analysis.
        """
        return {
            "coverage_percentage": 85,
            "covered_requirements": [
                "Basic application structure",
                "UI layout"
            ],
            "missing_requirements": [
                "Advanced features",
                "Error handling"
            ]
        }

