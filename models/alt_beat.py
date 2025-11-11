"""
ALT Beat Data Models
Typed data structures for ALT beats following research specifications
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Type definitions
ShotType = Literal[
    'extreme_closeup', 'closeup', 'medium_closeup', 
    'medium', 'medium_wide', 'wide', 'extreme_wide'
]

CameraMovement = Literal['static', 'pan', 'tilt', 'dolly', 'zoom', 'handheld']

EightPartBeat = Literal[
    'hook', 'inciting_event', 'first_plot_point', 'first_pinch_point',
    'midpoint', 'second_pinch_point', 'third_plot_point', 'climax'
]

Complexity = Literal['low', 'medium', 'high']


class ScriptContent(BaseModel):
    """Script content for a beat"""
    action: str
    dialogue: Optional[str] = None
    voiceover: Optional[str] = None
    on_screen_text: Optional[str] = None


class VisualRequirements(BaseModel):
    """Visual specifications for a beat"""
    shot_type: ShotType
    camera_movement: CameraMovement
    location: str
    lighting: str
    visual_keywords: list[str]
    complexity: Complexity


class AudioRequirements(BaseModel):
    """Audio specifications for a beat"""
    dialogue_present: bool
    sound_effects: list[str]
    music_mood: Optional[str] = None
    ambient: Optional[str] = None


class EmotionalContext(BaseModel):
    """Emotional arc information"""
    character_emotion: str
    audience_emotion: str
    emotional_arc_position: str
    intensity: int = Field(ge=1, le=10)


class NarrativeFunction(BaseModel):
    """Narrative purpose of the beat"""
    beat_type: str
    story_beat_number: int
    eight_part_position: EightPartBeat
    info_conveyed: str
    raises_question: Optional[str] = None
    answers_question: Optional[str] = None


class ProductionMetadata(BaseModel):
    """Production planning metadata"""
    estimated_complexity: Complexity
    requires_vfx: bool
    requires_custom_assets: bool
    suggested_tool_category: str
    reference_images: list[str] = Field(default_factory=list)


class AlternativeBeat(BaseModel):
    """Alternative version of a beat for branching"""
    alt_id: str
    condition: str
    script: ScriptContent
    emotional_context: EmotionalContext


class ALTBeat(BaseModel):
    """
    Complete ALT Beat structure
    Atomic narrative unit with complete metadata for AI video generation
    """
    # Identity
    beat_id: str
    scene_id: str
    sequence_order: int
    
    # Timing
    timecode_start: str
    timecode_end: str
    duration_seconds: int
    
    # Narrative
    story_question: str
    story_answer: str
    
    # Content
    script: ScriptContent
    
    # Requirements
    visual_requirements: VisualRequirements
    audio_requirements: AudioRequirements
    
    # Context
    emotional_context: EmotionalContext
    narrative_function: NarrativeFunction
    
    # Production
    production_metadata: ProductionMetadata
    
    # Alternatives
    alternatives: list[AlternativeBeat] = Field(default_factory=list)


class ScriptMetadata(BaseModel):
    """Metadata for complete script"""
    title: str
    duration_seconds: int
    target_audience: str
    primary_message: str
    tone: str
    style: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ScriptStructure(BaseModel):
    """Script structural organization"""
    total_beats: int
    eight_part_breakdown: dict[str, tuple[int, int]]
    act_1_beats: list[str] = Field(default_factory=list)
    act_2_beats: list[str] = Field(default_factory=list)
    act_3_beats: list[str] = Field(default_factory=list)


class Script(BaseModel):
    """
    Complete script with ALT beats
    Output from ScriptSmith agent
    """
    script_id: str
    vrd_ref: str
    mode: Literal['hitl', 'yolo']
    
    metadata: ScriptMetadata
    structure: ScriptStructure
    beats: list[ALTBeat]
    
    total_beat_count: int
    narrative_summary: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "script_id": "script_20251106_001",
                "vrd_ref": "explainer",
                "mode": "hitl",
                "metadata": {
                    "title": "Product Explainer Video",
                    "duration_seconds": 60,
                    "target_audience": "B2B decision makers",
                    "primary_message": "Solve problems efficiently",
                    "tone": "professional",
                    "style": "modern_realistic"
                },
                "total_beat_count": 8
            }
        }
