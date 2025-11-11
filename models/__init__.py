"""
Data Models Package
Pydantic models for type-safe agent communication
"""

from .alt_beat import (
    ALTBeat,
    Script,
    ScriptMetadata,
    ScriptStructure,
    ScriptContent,
    VisualRequirements,
    AudioRequirements,
    EmotionalContext,
    NarrativeFunction,
    ProductionMetadata,
    AlternativeBeat,
    ShotType,
    CameraMovement,
    EightPartBeat,
    Complexity,
)

from .shot import (
    Shot,
    ShotList,
    ShotComposition,
    ShotLighting,
    SetRequirements,
    TechnicalComplexity,
    StoryboardFrame,
    AssetSummary,
)

from .production_plan import (
    ProductionPlan,
    ShotPlan,
    Workflow,
    WorkflowStep,
    WorkflowSummary,
    CostBreakdown,
    TimelineEstimate,
)

__all__ = [
    # ALT Beat models
    'ALTBeat',
    'Script',
    'ScriptMetadata',
    'ScriptStructure',
    'ScriptContent',
    'VisualRequirements',
    'AudioRequirements',
    'EmotionalContext',
    'NarrativeFunction',
    'ProductionMetadata',
    'AlternativeBeat',
    'ShotType',
    'CameraMovement',
    'EightPartBeat',
    'Complexity',
    
    # Shot models
    'Shot',
    'ShotList',
    'ShotComposition',
    'ShotLighting',
    'SetRequirements',
    'TechnicalComplexity',
    'StoryboardFrame',
    'AssetSummary',
    
    # Production plan models
    'ProductionPlan',
    'ShotPlan',
    'Workflow',
    'WorkflowStep',
    'WorkflowSummary',
    'CostBreakdown',
    'TimelineEstimate',
]
