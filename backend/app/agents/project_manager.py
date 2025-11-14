"""
Project Manager Agent

Breaks down user prompt into tasks and coordinates specialist agents.
"""
from typing import List, Dict, Any
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
        
        for task in tasks:
            task_type = task.get("type")
            
            if task_type == "code":
                results["code"] = await self.code_agent.generate_code(task["description"])
            elif task_type == "ui":
                results["ui"] = await self.ui_agent.generate_ui_design(task["description"])
        
        # Get usability feedback
        results["usability_feedback"] = await self.usability_agent.review_ux(
            code_result=results["code"],
            ui_result=results["ui"]
        )
        
        return results
    
    async def coordinate_generation(self, prompt: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Main coordination method that iterates until Reviewer approves.
        
        Returns final approved result or raises exception if max iterations reached.
        """
        tasks = await self.break_down_prompt(prompt)
        
        for iteration in range(max_iterations):
            # Execute tasks
            results = await self.execute_tasks(tasks)
            
            # Get reviewer feedback
            review = await self.reviewer_agent.review_completeness(
                prompt=prompt,
                results=results,
                iteration=iteration
            )
            
            if review["approved"]:
                return {
                    "approved": True,
                    "results": results,
                    "review": review,
                    "iterations": iteration + 1
                }
            
            # If not approved, refine tasks based on feedback
            if iteration < max_iterations - 1:
                tasks = await self._refine_tasks(tasks, review["issues"])
        
        # Max iterations reached without approval
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

