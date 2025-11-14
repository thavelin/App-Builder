"""
Project Manager Agent

Breaks down user prompt into tasks and coordinates specialist agents.
"""
from typing import List, Dict, Any, Optional
from app.agents.code_agent import CodeAgent
from app.agents.ui_agent import UIAgent
from app.agents.usability_agent import UsabilityAgent
from app.agents.reviewer_agent import ReviewerAgent


class ProjectManagerAgent:
    """
    Orchestrates the multi-agent workflow by:
    1. Breaking down the user prompt into tasks
    2. Calling specialist agents as tools
    3. Iterating until Reviewer gives pass/fail
    """
    
    def __init__(self):
        self.code_agent = CodeAgent()
        self.ui_agent = UIAgent()
        self.usability_agent = UsabilityAgent()
        self.reviewer_agent = ReviewerAgent()
    
    async def break_down_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Analyze the prompt and break it down into actionable tasks.
        
        Returns a list of task dictionaries with type, description, and priority.
        """
        # TODO: Implement prompt analysis using OpenAI
        # For now, return placeholder structure
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
        Execute tasks by delegating to appropriate specialist agents.
        
        Returns a combined result from all agents.
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
        
        # Get usability feedback
        print("  [ProjectManager] → Calling UsabilityAgent.review_ux()...", flush=True)
        results["usability_feedback"] = await self.usability_agent.review_ux(
            code_result=results["code"],
            ui_result=results["ui"]
        )
        if results["usability_feedback"]:
            print(f"  [UsabilityAgent] ✓ Provided UX feedback", flush=True)
        
        return results
    
    async def coordinate_generation(
        self,
        prompt: str,
        max_iterations: int = 3,
        review_threshold: int = 80,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Main coordination method that iterates until Reviewer approves.
        
        Returns final approved result or raises exception if max iterations reached.
        """
        # Set the review threshold on the reviewer agent
        self.reviewer_agent.approval_threshold = review_threshold
        print(f"  [ProjectManager] Review threshold set to: {review_threshold}", flush=True)
        
        if attachments:
            print(f"  [ProjectManager] Received {len(attachments)} attachment(s) (not yet processed)", flush=True)
        
        print("  [ProjectManager] Breaking down prompt into tasks...", flush=True)
        tasks = await self.break_down_prompt(prompt)
        print(f"  [ProjectManager] Created {len(tasks)} tasks", flush=True)
        
        for iteration in range(max_iterations):
            print(f"\n  [ProjectManager] === Iteration {iteration + 1}/{max_iterations} ===", flush=True)
            
            # Execute tasks
            results = await self.execute_tasks(tasks)
            
            # Get reviewer feedback
            print("  [ProjectManager] → Calling ReviewerAgent.review_completeness()...", flush=True)
            review = await self.reviewer_agent.review_completeness(
                prompt=prompt,
                results=results,
                iteration=iteration
            )
            
            score = review.get("score", 0)
            approved = review.get("approved", False)
            issues = review.get("issues", [])
            
            print(f"  [ReviewerAgent] Review score: {score}/100, Approved: {approved}", flush=True)
            if issues:
                print(f"  [ReviewerAgent] Issues found: {len(issues)}", flush=True)
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"    - {issue}", flush=True)
            
            if review["approved"]:
                print(f"  [ProjectManager] ✓ Approved after {iteration + 1} iteration(s)", flush=True)
                return {
                    "approved": True,
                    "results": results,
                    "review": review,
                    "iterations": iteration + 1
                }
            
            # If not approved, refine tasks based on feedback
            if iteration < max_iterations - 1:
                print(f"  [ProjectManager] Not approved. Refining tasks for next iteration...", flush=True)
                tasks = await self._refine_tasks(tasks, review["issues"])
        
        # Max iterations reached without approval
        print(f"  [ProjectManager] ✗ Maximum iterations ({max_iterations}) reached without approval", flush=True)
        return {
            "approved": False,
            "results": results,
            "review": review,
            "iterations": max_iterations,
            "error": "Maximum iterations reached without approval"
        }
    
    async def _refine_tasks(self, tasks: List[Dict[str, Any]], issues: List[str]) -> List[Dict[str, Any]]:
        """
        Refine tasks based on reviewer feedback.
        
        TODO: Implement intelligent task refinement.
        """
        # For now, just add new tasks based on issues
        new_tasks = tasks.copy()
        for issue in issues:
            new_tasks.append({
                "type": "code",  # Default to code fixes
                "description": f"Fix: {issue}",
                "priority": "medium"
            })
        return new_tasks

