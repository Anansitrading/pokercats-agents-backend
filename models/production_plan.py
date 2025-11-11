"""
Production Plan Data Models
Typed data structures for VideoSolver output
"""

from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowStep(BaseModel):
    """Single step in a generation workflow"""
    step: int
    tool: str
    purpose: str
    workflow_type: Literal['text_to_video', 'image_to_video', 'video_to_video']
    duration_seconds: int = 0
    estimated_time_seconds: int
    cost_usd: float


class Workflow(BaseModel):
    """Complete workflow for generating a shot"""
    workflow_id: str
    workflow_name: str
    steps: list[WorkflowStep]
    total_cost: float
    total_time_seconds: int
    quality_score: float


class ShotPlan(BaseModel):
    """Production plan for a single shot"""
    shot_id: str
    shot_description: str
    recommended_workflow: Workflow
    alternative_workflows: list[Workflow] = Field(default_factory=list)
    production_notes: list[str] = Field(default_factory=list)


class WorkflowSummary(BaseModel):
    """Summary of workflows used"""
    total_unique_tools: int
    primary_tools: list[tuple[str, float]]
    workflow_types: dict[str, int]


class CostBreakdown(BaseModel):
    """Cost analysis"""
    by_tool: dict[str, float]


class TimelineEstimate(BaseModel):
    """Timeline estimation"""
    parallel_generation: bool = True
    sequential_time_minutes: float
    parallel_time_minutes: float
    post_processing_minutes: int = 30


class ProductionPlan(BaseModel):
    """
    Complete production plan
    Output from VideoSolver agent
    """
    production_plan_id: str
    shot_list_ref: str
    mode: Literal['hitl', 'yolo']
    total_estimated_cost_usd: float
    total_estimated_time_minutes: float
    
    shot_plans: list[ShotPlan]
    workflow_summary: WorkflowSummary
    cost_breakdown: CostBreakdown
    timeline_estimate: TimelineEstimate
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
