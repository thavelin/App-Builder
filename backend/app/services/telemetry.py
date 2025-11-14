"""
Telemetry Service

Lightweight logging for app generation runs.
Stores run data as JSON lines for analysis.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class TelemetryService:
    """Service for logging generation runs."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "generation_runs.jsonl"
    
    def log_run(
        self,
        job_id: str,
        prompt: str,
        app_spec: Dict[str, Any],
        review: Dict[str, Any],
        approved: bool,
        iterations: int,
        duration_seconds: Optional[float] = None
    ):
        """
        Log a generation run to JSONL file.
        
        Args:
            job_id: Unique job identifier
            prompt: Original user prompt
            app_spec: AppSpec dictionary
            review: Final review results
            approved: Whether the build was approved
            iterations: Number of iterations
            duration_seconds: Optional duration in seconds
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job_id,
            "input": {
                "prompt": prompt[:500],  # Truncate very long prompts
                "prompt_length": len(prompt)
            },
            "spec": {
                "goal": app_spec.get("goal", "")[:200],
                "complexity": app_spec.get("complexity_level", "unknown"),
                "features_count": len(app_spec.get("core_features", [])),
                "views_count": len(app_spec.get("views", [])),
                "entities_count": len(app_spec.get("entities", []))
            },
            "output": {
                "approved": approved,
                "iterations": iterations,
                "score": review.get("score", 0),
                "requirements_match": review.get("requirements_match", 0),
                "functional_completeness": review.get("functional_completeness", 0),
                "ui_ux_reasonableness": review.get("ui_ux_reasonableness", 0),
                "ready_for_user": review.get("ready_for_user", False),
                "red_flags_count": len(review.get("obvious_red_flags", [])),
                "missing_features_count": len(review.get("missing_core_features", []))
            }
        }
        
        if duration_seconds is not None:
            log_entry["duration_seconds"] = duration_seconds
        
        # Append to JSONL file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"[Telemetry] Failed to log run: {e}", flush=True)


# Global instance
telemetry = TelemetryService()

