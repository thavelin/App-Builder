"""
Project Manager Agent

Coordinates the multi-agent workflow using AppSpec as the single source of truth.
"""
from typing import List, Dict, Any, Optional
from app.agents.code_agent import CodeAgent
from app.agents.ui_agent import UIAgent
from app.agents.usability_agent import UsabilityAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.requirements_agent import RequirementsAgent
from app.schemas.app_spec import AppSpec


class ProjectManagerAgent:
    """
    Orchestrates the multi-agent workflow by:
    1. Breaking down the user prompt into tasks
    2. Calling specialist agents as tools
    3. Iterating until Reviewer gives pass/fail
    """
    
    def __init__(self):
        self.requirements_agent = RequirementsAgent()
        self.code_agent = CodeAgent()
        self.ui_agent = UIAgent()
        self.usability_agent = UsabilityAgent()
        self.reviewer_agent = ReviewerAgent()
    
    # Legacy methods kept for backward compatibility
    async def break_down_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Legacy method - kept for backward compatibility.
        New workflow uses AppSpec extraction instead.
        """
        return [
            {
                "type": "code",
                "description": f"Generate code for: {prompt}",
                "priority": "high"
            },
            {
                "type": "ui",
                "description": f"Design UI for: {prompt}",
                "priority": "high"
            }
        ]
    
    async def execute_tasks(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Legacy method - kept for backward compatibility.
        New workflow uses coordinate_generation with AppSpec.
        """
        results = {
            "code": None,
            "ui": None,
            "usability_feedback": None
        }
        
        print("  [ProjectManager] Executing tasks with specialist agents...", flush=True)
        
        for task in tasks:
            task_type = task.get("type")
            
            if task_type == "code":
                print("  [ProjectManager] → Calling CodeAgent.generate_code()...", flush=True)
                results["code"] = await self.code_agent.generate_code(task["description"])
                if results["code"]:
                    file_count = len(results["code"].get("files", []))
                    print(f"  [CodeAgent] ✓ Generated {file_count} code files", flush=True)
            elif task_type == "ui":
                print("  [ProjectManager] → Calling UIAgent.generate_ui_design()...", flush=True)
                results["ui"] = await self.ui_agent.generate_ui_design(task["description"])
                if results["ui"]:
                    print(f"  [UIAgent] ✓ Generated UI design", flush=True)
        
        return results
    
    async def coordinate_generation(
        self,
        prompt: str,
        max_iterations: int = 3,
        review_threshold: int = 80,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Main coordination method using AppSpec-driven workflow.
        
        Flow:
        1. Extract AppSpec from prompt (Requirements Agent)
        2. Generate UX plan from AppSpec (UI Agent)
        3. Generate code from AppSpec + UX plan (Code Agent)
        4. Review against AppSpec (Reviewer Agent)
        5. Iterate with repair briefs if needed
        
        Returns final approved result with AppSpec, code, and review.
        """
        # Set the review threshold on the reviewer agent
        self.reviewer_agent.approval_threshold = review_threshold
        print(f"  [ProjectManager] Review threshold set to: {review_threshold}", flush=True)
        
        # Step 1: Extract AppSpec from prompt
        print("  [ProjectManager] Step 1: Extracting AppSpec from prompt...", flush=True)
        app_spec = await self.requirements_agent.extract_spec(prompt, attachments)
        print(f"  [ProjectManager] ✓ AppSpec extracted: {app_spec.complexity_level.value} complexity", flush=True)
        print(f"    Goal: {app_spec.goal}", flush=True)
        print(f"    Features: {', '.join(app_spec.core_features[:3])}{'...' if len(app_spec.core_features) > 3 else ''}", flush=True)
        
        # Step 2: Generate UX plan from AppSpec
        print("  [ProjectManager] Step 2: Generating UX plan from AppSpec...", flush=True)
        ux_plan = await self.ui_agent.generate_ux_plan(app_spec)
        print(f"  [ProjectManager] ✓ UX plan generated with {len(ux_plan.get('views', []))} views", flush=True)
        
        # Initialize iteration state
        previous_code = None
        iteration_history = []
        
        # Step 3-5: Iterate code generation and review
        for iteration in range(max_iterations):
            print(f"\n  [ProjectManager] === Iteration {iteration + 1}/{max_iterations} ===", flush=True)
            
            # Step 3: Generate code
            print("  [ProjectManager] Step 3: Generating code from AppSpec and UX plan...", flush=True)
            repair_brief = None
            if iteration > 0 and previous_code:
                # Create repair brief from previous review
                repair_brief = self._create_repair_brief(iteration_history[-1])
                print(f"  [ProjectManager] Repair brief: {repair_brief[:100]}...", flush=True)
            
            code_result = await self.code_agent.generate_code_from_spec(
                app_spec=app_spec,
                ux_plan=ux_plan,
                previous_code=previous_code,
                repair_brief=repair_brief
            )
            previous_code = code_result
            
            file_count = len(code_result.get("files", []))
            print(f"  [ProjectManager] ✓ Generated {file_count} files", flush=True)
            
            # Step 4: Review against AppSpec
            print("  [ProjectManager] Step 4: Reviewing code against AppSpec...", flush=True)
            review = await self.reviewer_agent.review_against_spec(
                app_spec=app_spec,
                code_result=code_result,
                ux_plan=ux_plan,
                iteration=iteration
            )
            
            score = review.get("score", 0)
            approved = review.get("approved", False)
            ready_for_user = review.get("ready_for_user", False)
            red_flags = review.get("obvious_red_flags", [])
            improvements = review.get("suggested_improvements", [])
            
            print(f"  [ReviewerAgent] Score: {score:.1f}/100, Approved: {approved}, Ready: {ready_for_user}", flush=True)
            if red_flags:
                print(f"  [ReviewerAgent] Red flags: {len(red_flags)}", flush=True)
                for flag in red_flags[:3]:
                    print(f"    - {flag}", flush=True)
            if improvements:
                print(f"  [ReviewerAgent] Suggested improvements: {len(improvements)}", flush=True)
                for imp in improvements[:3]:
                    print(f"    - {imp}", flush=True)
            
            # Store iteration history
            iteration_history.append({
                "iteration": iteration + 1,
                "code_result": code_result,
                "review": review
            })
            
            # Step 5: Check if approved
            if approved and ready_for_user:
                print(f"  [ProjectManager] ✓ Approved after {iteration + 1} iteration(s)", flush=True)
                return {
                    "approved": True,
                    "app_spec": app_spec.to_dict(),
                    "ux_plan": ux_plan,
                    "results": {
                        "code": code_result,
                        "ui": ux_plan,  # UX plan serves as UI design
                        "usability_feedback": None  # Can be added later if needed
                    },
                    "review": review,
                    "iterations": iteration + 1,
                    "iteration_history": iteration_history
                }
            
            # If not approved and more iterations available, continue
            if iteration < max_iterations - 1:
                print(f"  [ProjectManager] Not approved. Preparing for next iteration...", flush=True)
            else:
                print(f"  [ProjectManager] Max iterations reached. Returning best available version.", flush=True)
        
        # Max iterations reached - return best available version
        best_iteration = iteration_history[-1] if iteration_history else None
        if best_iteration:
            final_code = best_iteration["code_result"]
            final_review = best_iteration["review"]
        else:
            final_code = previous_code or {}
            final_review = review
        
        print(f"  [ProjectManager] ✗ Maximum iterations ({max_iterations}) reached", flush=True)
        return {
            "approved": False,
            "app_spec": app_spec.to_dict(),
            "ux_plan": ux_plan,
            "results": {
                "code": final_code,
                "ui": ux_plan,
                "usability_feedback": None
            },
            "review": final_review,
            "iterations": max_iterations,
            "iteration_history": iteration_history,
            "error": "Maximum iterations reached without approval"
        }
    
    def _create_repair_brief(self, previous_iteration: Dict[str, Any]) -> str:
        """
        Create a concise repair brief from previous review feedback.
        
        Summarizes what needs to be fixed for the next iteration.
        """
        review = previous_iteration.get("review", {})
        
        brief_parts = []
        
        # Red flags (critical issues)
        red_flags = review.get("obvious_red_flags", [])
        if red_flags:
            brief_parts.append("CRITICAL ISSUES TO FIX:")
            for flag in red_flags[:5]:  # Top 5 red flags
                brief_parts.append(f"- {flag}")
        
        # Missing core features
        missing_features = review.get("missing_core_features", [])
        if missing_features:
            brief_parts.append("\nMISSING CORE FEATURES:")
            for feature in missing_features[:5]:
                brief_parts.append(f"- {feature}")
        
        # Suggested improvements
        improvements = review.get("suggested_improvements", [])
        if improvements:
            brief_parts.append("\nSUGGESTED IMPROVEMENTS:")
            for imp in improvements[:5]:  # Top 5 improvements
                brief_parts.append(f"- {imp}")
        
        # Overall notes
        notes = review.get("notes", "")
        if notes:
            brief_parts.append(f"\nNOTES: {notes}")
        
        return "\n".join(brief_parts) if brief_parts else "Improve code quality and completeness."
    
    async def _refine_tasks(self, tasks: List[Dict[str, Any]], issues: List[str]) -> List[Dict[str, Any]]:
        """
        Legacy method - kept for backward compatibility.
        New workflow uses repair briefs instead.
        """
        new_tasks = tasks.copy()
        for issue in issues:
            new_tasks.append({
                "type": "code",
                "description": f"Fix: {issue}",
                "priority": "medium"
            })
        return new_tasks

