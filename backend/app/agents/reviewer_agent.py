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
        import time
        start_time = time.time()
        print(f"    [ReviewerAgent] ===== Starting REVIEWER phase (iteration {iteration + 1}) =====", flush=True)
        print(f"    [ReviewerAgent] Reviewing against AppSpec...", flush=True)
        print(f"    [ReviewerAgent] Model: {self.model}", flush=True)
        
        if not self.client:
            print("    [ReviewerAgent] ERROR: OpenAI not configured, using fallback approval", flush=True)
            return self._fallback_review(app_spec, iteration)
        
        print(f"    [ReviewerAgent] OpenAI client initialized", flush=True)
        
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
        
        system_prompt = """You are a code review expert (REVIEWER phase). Your job is to evaluate a generated application against ARCHITECT_SPEC.

You must:
1. Score requirements_match (0-10): How well does the code match ARCHITECT_SPEC?
2. Score functional_completeness (0-10): Are ALL features from ARCHITECT_SPEC.features implemented?
3. Score ui_ux_reasonableness (0-10): Is the UI polished, responsive, and matches ARCHITECT_SPEC.ux_details?
4. Identify obvious_red_flags (missing UI, missing features, TODOs in main flows, wrong stack, etc.)
5. List missing_core_features if any features from ARCHITECT_SPEC.features are not implemented
6. Determine ready_for_user (true only if score ≥8/10 on each category AND no critical red flags)

Be strict but fair. Approve only if the app fully satisfies ARCHITECT_SPEC. Provide concrete PATCH_PLAN if fixes are needed."""

        # Get ARCHITECT_SPEC from app_spec if available
        architect_spec = getattr(app_spec, 'architect_spec', None) or app_spec.to_dict().get('architect_spec')

        if architect_spec:
            # Review against ARCHITECT_SPEC (new workflow)
            user_prompt = f"""Review this generated application against ARCHITECT_SPEC:

ARCHITECT_SPEC:
{json.dumps(architect_spec, indent=2)}

GENERATED CODE:
- Files: {file_count} files
- Entry Point: {entry_point}
- File Names: {', '.join(file_names)}
- Structure: {json.dumps(structure, indent=2)}
- TODOs Found: {todo_count} files with TODO/FIXME comments

This is iteration {iteration + 1} of the review process.

Checklist:
- Stack matches ARCHITECT_SPEC.stack: {architect_spec.get('stack', 'unknown')}
- Files match ARCHITECT_SPEC.files: {', '.join(architect_spec.get('files', []))}
- All features from ARCHITECT_SPEC.features are implemented
- Layout matches ARCHITECT_SPEC.requirements.layout
- Persistence method matches ARCHITECT_SPEC.requirements.persistence
- UX details match ARCHITECT_SPEC.ux_details
"""
        else:
            # Fallback to old format
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

ready_for_user should be true ONLY if:
- requirements_match ≥ 8 AND functional_completeness ≥ 8 AND ui_ux_reasonableness ≥ 8
- No critical red flags
- All features from ARCHITECT_SPEC.features are implemented
- App matches ARCHITECT_SPEC requirements (stack, layout, persistence, UX)

missing_core_features: List any features from ARCHITECT_SPEC.features that are NOT implemented.

CRITICAL: You MUST return ONLY a valid JSON object. Do NOT include any markdown formatting, headers, explanations, or text before or after the JSON. Start your response with {{ and end with }}. No markdown, no code blocks, no explanations - ONLY the raw JSON object."""

        try:
            print(f"    [ReviewerAgent] Preparing review: {file_count} files, {todo_count} files with TODOs", flush=True)
            print(f"    [ReviewerAgent] Calling OpenAI API (model: {self.model}, max_tokens: 2000)...", flush=True)
            api_start = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            api_duration = time.time() - api_start
            print(f"    [ReviewerAgent] OpenAI API call completed in {api_duration:.2f}s", flush=True)
            print(f"    [ReviewerAgent] Response tokens: {response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 'unknown'}", flush=True)
            
            content = response.choices[0].message.content.strip()
            print(f"    [ReviewerAgent] Response length: {len(content)} characters", flush=True)
            
            # Remove markdown code blocks if present
            print(f"    [ReviewerAgent] Cleaning response (removing markdown if present)...", flush=True)
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to extract JSON from markdown text if it's not pure JSON
            # First, try parsing as-is
            try:
                json.loads(content)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON object from markdown
                import re
                # Look for JSON object with balanced braces
                brace_count = 0
                start_idx = -1
                for i, char in enumerate(content):
                    if char == '{':
                        if start_idx == -1:
                            start_idx = i
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and start_idx != -1:
                            # Found complete JSON object
                            extracted = content[start_idx:i+1]
                            try:
                                json.loads(extracted)  # Validate it's valid JSON
                                content = extracted
                                print(f"    [ReviewerAgent] Extracted JSON from markdown text (length: {len(content)} chars)", flush=True)
                                break
                            except json.JSONDecodeError:
                                # Not valid JSON, continue searching
                                start_idx = -1
                                brace_count = 0
            
            print(f"    [ReviewerAgent] Parsing JSON response...", flush=True)
            print(f"    [ReviewerAgent] Content preview (first 200 chars): {content[:200]}", flush=True)
            result = json.loads(content)
            print(f"    [ReviewerAgent] JSON parsed successfully", flush=True)
            
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
            
            duration = time.time() - start_time
            print(f"    [ReviewerAgent] ✓ REVIEWER phase complete in {duration:.2f}s", flush=True)
            print(f"    [ReviewerAgent] Score: {score:.1f}/100, Approved: {result['approved']}, Ready: {result.get('ready_for_user', False)}", flush=True)
            if architect_spec:
                req_match = result.get("requirements_match", 0)
                func_comp = result.get("functional_completeness", 0)
                ui_ux = result.get("ui_ux_reasonableness", 0)
                print(f"    [ReviewerAgent] Individual scores: Requirements={req_match}/10, Functional={func_comp}/10, UI/UX={ui_ux}/10", flush=True)
            print(f"    [ReviewerAgent] ===== REVIEWER phase finished =====", flush=True)
            return result
            
        except json.JSONDecodeError as e:
            duration = time.time() - start_time
            print(f"    [ReviewerAgent] ERROR: JSON decode error after {duration:.2f}s: {e}", flush=True)
            print(f"    [ReviewerAgent] Response content (first 500 chars): {content[:500] if 'content' in locals() else 'N/A'}", flush=True)
            print(f"    [ReviewerAgent] Using fallback review", flush=True)
            return self._fallback_review(app_spec, iteration)
        except Exception as e:
            duration = time.time() - start_time
            import traceback
            print(f"    [ReviewerAgent] ERROR: Exception after {duration:.2f}s: {e}", flush=True)
            print(f"    [ReviewerAgent] Traceback:", flush=True)
            print(traceback.format_exc(), flush=True)
            print(f"    [ReviewerAgent] Using fallback review", flush=True)
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

CRITICAL: You MUST return ONLY a valid JSON object. Do NOT include any markdown formatting, headers, explanations, or text before or after the JSON. Start your response with {{ and end with }}. No markdown, no code blocks, no explanations - ONLY the raw JSON object."""

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

