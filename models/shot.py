"""
Shot Data Models
Typed data structures for shot specifications from ShotMaster
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ShotComposition(BaseModel):
    """Composition guidelines for a shot"""
    rule_of_thirds: bool = True
    focal_point: str
    depth_of_field: Literal['shallow', 'deep']


class ShotLighting(BaseModel):
    """Lighting specifications"""
    time_of_day: str
    mood: str
    key_light: str
    practical_lights: list[str] = Field(default_factory=list)


class SetRequirements(BaseModel):
    """Set and location requirements"""
    location_type: str
    props: list[str] = Field(default_factory=list)
    set_dressing: str


class TechnicalComplexity(BaseModel):
    """Technical complexity metrics"""
    complexity_score: int = Field(ge=1, le=10)
    requires_motion: bool
    requires_vfx: bool
    requires_compositing: bool
    estimated_generation_time_seconds: int


class StoryboardFrame(BaseModel):
    """Storyboard frame description"""
    description: str
    reference_image_prompt: str
    thumbnail_url: Optional[str] = None


class Shot(BaseModel):
    """
    Complete shot specification
    Output from ShotMaster agent
    """
    shot_id: str
    beat_ref: str
    shot_number: int
    shot_type: str
    subject: str
    camera_angle: str
    camera_movement: str
    duration_seconds: int
    frame_rate: int = 24
    resolution: str = "1080p"
    
    composition: ShotComposition
    lighting: ShotLighting
    set_requirements: SetRequirements
    technical_complexity: TechnicalComplexity
    storyboard_frame: StoryboardFrame


class AssetSummary(BaseModel):
    """Summary of required assets"""
    total_unique_locations: int
    total_unique_shot_types: int
    total_character_shots: int
    vfx_shots: int
    requires_custom_models: bool
    estimated_total_time_minutes: float


class ShotList(BaseModel):
    """
    Complete shot list
    Output from ShotMaster agent
    """
    shot_list_id: str
    script_ref: str
    mode: Literal['hitl', 'yolo']
    total_shots: int
    total_scenes: int
    
    shots: list[Shot]
    asset_summary: AssetSummary
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
