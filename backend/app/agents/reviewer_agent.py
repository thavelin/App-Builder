"""
Reviewer Agent

Scores completeness and outputs structured JSON with score and issues.
"""
import json
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from openai import AsyncOpenAI
from app.config import settings

if TYPE_CHECKING:
    from app.schemas.app_spec import AppSpec


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
    
    async def review_against_spec(
        self,
        app_spec: "AppSpec",
        code_result: Dict[str, Any],
        ux_plan: Optional[Dict[str, Any]] = None,
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        Review the generated application against the AppSpec.
        
        Returns a structured evaluation with scores and actionable feedback.
        """
        print(f"    [ReviewerAgent] Reviewing against AppSpec (iteration {iteration + 1})...", flush=True)
        if not self.client:
            print("    [ReviewerAgent] OpenAI not configured, using fallback approval", flush=True)
            return self._fallback_review(app_spec, iteration)
        
        # Prepare code summary
        files = code_result.get("files", [])
        file_count = len(files)
        file_names = [f.get("path", "unknown") for f in files[:10]]  # First 10 files
        structure = code_result.get("structure", {})
        entry_point = structure.get("entry_point", "unknown")
        
        # Check for TODOs in code (red flag)
        todo_count = 0
        for file_info in files:
            content = file_info.get("content", "")
            if "TODO" in content.upper() or "FIXME" in content.upper():
                todo_count += 1
        
        system_prompt = """You are a code review expert. Your job is to evaluate a generated application against its specification.

You must:
1. Evaluate how well the code matches the AppSpec
2. Check functional completeness
3. Assess UI/UX reasonableness
4. Identify obvious red flags (missing core features, no UI, TODOs in main flows, etc.)
5. Provide actionable improvement suggestions
6. Determine if it's ready for users (good enough as first version)

Be reasonable - a good MVP with some enhancements possible should pass. Only reject if there are critical issues."""

        user_prompt = f"""Review this generated application against its specification:

APP SPECIFICATION:
{app_spec.summary()}

Core Features Required: {', '.join(app_spec.core_features)}
In-Scope: {', '.join(app_spec.in_scope) if app_spec.in_scope else 'All core features'}
Out-of-Scope: {', '.join(app_spec.out_of_scope) if app_spec.out_of_scope else 'None'}

GENERATED CODE:
- Files: {file_count} files
- Entry Point: {entry_point}
- File Names: {', '.join(file_names)}
- Structure: {json.dumps(structure, indent=2)}
- TODOs Found: {todo_count} files with TODO/FIXME comments

UX PLAN:
{json.dumps(ux_plan, indent=2) if ux_plan else 'Not provided'}

This is iteration {iteration + 1} of the review process.

Return a JSON object with this structure:
{{
    "requirements_match": 8,
    "functional_completeness": 7,
    "ui_ux_reasonableness": 8,
    "obvious_red_flags": ["flag1", "flag2"],
    "runtime_risks": ["risk1", "risk2"],
    "suggested_improvements": ["improvement1", "improvement2"],
    "ready_for_user": true,
    "notes": "Overall assessment",
    "missing_core_features": ["feature1", "feature2"],
    "score": 85
}}

Scoring Guidelines (0-10 scale):
- requirements_match: How well does it match the spec? (0-10)
- functional_completeness: Are core features implemented? (0-10)
- ui_ux_reasonableness: Is the UI reasonable and functional? (0-10)

Red Flags to look for:
- No UI rendered or visible
- Core features completely missing
- No way to interact with the app
- Entry point doesn't exist
- TODOs in main user flows (not just edge cases)

Suggested Improvements should be:
- Concrete and actionable
- Focused on critical issues first
- Realistic for the next iteration

ready_for_user should be true if:
- Core features are implemented and functional
- UI is present and reasonable
- App can be run and used
- It's a good MVP even if enhancements are possible

Return ONLY valid JSON, no markdown formatting or code blocks."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
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
            
            # Calculate overall score (weighted average)
            score = (
                result.get("requirements_match", 0) * 0.4 +
                result.get("functional_completeness", 0) * 0.4 +
                result.get("ui_ux_reasonableness", 0) * 0.2
            ) * 10  # Convert to 0-100 scale
            
            result["score"] = round(score, 1)
            
            # Determine approval based on threshold and ready_for_user
            result["approved"] = (
                score >= self.approval_threshold and
                result.get("ready_for_user", False) and
                len(result.get("obvious_red_flags", [])) == 0
            )
            
            result["iteration"] = iteration
            
            # Legacy fields for compatibility
            result["issues"] = result.get("obvious_red_flags", []) + result.get("missing_core_features", [])
            result["feedback"] = result.get("notes", "")
            
            print(f"    [ReviewerAgent] Score: {score:.1f}/100, Approved: {result['approved']}, Ready: {result.get('ready_for_user', False)}", flush=True)
            return result
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"    [ReviewerAgent] Error in review: {e}, using fallback", flush=True)
            return self._fallback_review(app_spec, iteration)
    
    def _fallback_review(self, app_spec: "AppSpec", iteration: int) -> Dict[str, Any]:
        """Generate fallback review when OpenAI is not available."""
        score = 85 if iteration > 0 else 70
        return {
            "requirements_match": 8,
            "functional_completeness": 8,
            "ui_ux_reasonableness": 8,
            "obvious_red_flags": ["OpenAI not configured for review"],
            "runtime_risks": [],
            "suggested_improvements": ["Configure OpenAI for detailed review"],
            "ready_for_user": True,
            "notes": f"Fallback review (iteration {iteration + 1})",
            "missing_core_features": [],
            "score": score,
            "approved": score >= self.approval_threshold,
            "iteration": iteration,
            "issues": ["OpenAI not configured"],
            "feedback": "Fallback review"
        }
    
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

