"""
AppSpec Schema

Generic, language-agnostic specification structure for any application.
This serves as the single source of truth for what an app should be.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ComplexityLevel(str, Enum):
    """Complexity level of the application."""
    TINY = "tiny"  # Very simple, single-page apps
    SMALL = "small"  # Simple apps with a few features
    MEDIUM = "medium"  # Moderate complexity with multiple features
    AMBITIOUS = "ambitious"  # Complex apps (will be scoped down to MVP)


class Entity(BaseModel):
    """Represents a data entity in the application."""
    name: str = Field(..., description="Name of the entity (e.g., 'Task', 'User', 'Product')")
    fields: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of fields, each with 'name' and 'type' keys"
    )
    description: Optional[str] = Field(None, description="Description of what this entity represents")


class View(BaseModel):
    """Represents a view/page/screen in the application."""
    name: str = Field(..., description="Name of the view (e.g., 'Dashboard', 'TaskList', 'Settings')")
    purpose: str = Field(..., description="What this view is for")
    primary_actions: List[str] = Field(
        default_factory=list,
        description="Main actions users can perform on this view"
    )
    description: Optional[str] = Field(None, description="Additional details about this view")


class UXPlan(BaseModel):
    """Structured UX plan derived from AppSpec."""
    views: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of views with layout sections and component lists"
    )
    navigation_flow: Dict[str, Any] = Field(
        default_factory=dict,
        description="How users navigate between views"
    )
    component_library: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Reusable components needed across views"
    )


class AppSpec(BaseModel):
    """
    Generic application specification.
    
    This structure represents what an app should be, regardless of domain or technology stack.
    It serves as the single source of truth throughout the generation process.
    """
    goal: str = Field(
        ...,
        description="Short summary of what the user wants to build"
    )
    user_type: str = Field(
        ...,
        description="Who the app is for (e.g., 'individual users', 'small business owners', 'developers')"
    )
    core_features: List[str] = Field(
        default_factory=list,
        description="High-level features the app must have (e.g., 'add task', 'edit task', 'view dashboard')"
    )
    entities: List[Entity] = Field(
        default_factory=list,
        description="Data entities in the application"
    )
    views: List[View] = Field(
        default_factory=list,
        description="Views/pages/screens in the application"
    )
    stack_preferences: Optional[List[str]] = Field(
        None,
        description="Technology stack hints from user (e.g., ['Next.js', 'React'], ['plain HTML/JS'], ['FastAPI'])"
    )
    non_functional_requirements: List[str] = Field(
        default_factory=list,
        description="Non-functional requirements (e.g., 'mobile-first', 'dark mode', 'offline-friendly')"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Constraints (e.g., 'no external DB', 'must run as static site', 'no backend required')"
    )
    complexity_level: ComplexityLevel = Field(
        ComplexityLevel.SMALL,
        description="Estimated complexity level"
    )
    scope_notes: Optional[str] = Field(
        None,
        description="Notes about scope adjustments (e.g., if original request was too ambitious and was scoped down)"
    )
    in_scope: List[str] = Field(
        default_factory=list,
        description="Explicitly in-scope features for this build"
    )
    out_of_scope: List[str] = Field(
        default_factory=list,
        description="Explicitly out-of-scope features (for future iterations)"
    )
    architect_spec: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw ARCHITECT_SPEC JSON (internal use, not part of standard spec)"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert AppSpec to dictionary for serialization."""
        data = self.model_dump()
        # Include architect_spec if present
        if hasattr(self, 'architect_spec') and self.architect_spec:
            data['architect_spec'] = self.architect_spec
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSpec":
        """Create AppSpec from dictionary."""
        return cls(**data)

    def summary(self) -> str:
        """Generate a human-readable summary of the spec."""
        lines = [
            f"Goal: {self.goal}",
            f"User Type: {self.user_type}",
            f"Complexity: {self.complexity_level.value}",
            f"Core Features: {', '.join(self.core_features)}",
            f"Views: {', '.join([v.name for v in self.views])}",
            f"Entities: {', '.join([e.name for e in self.entities])}",
        ]
        if self.scope_notes:
            lines.append(f"Scope Notes: {self.scope_notes}")
        return "\n".join(lines)

