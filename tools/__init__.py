"""
Tools Package
Reusable tool functions for agents
"""

from .alt_beat_generator import (
    generate_alt_beats,
    validate_alt_beats_timing,
    calculate_eight_part_timing,
    BEAT_TEMPLATES
)

from .clarifying_questions import (
    ask_clarifying_questions,
    apply_clarifications_to_vrd
)

from .shot_planner import (
    generate_shot_list,
    SHOT_TYPE_MAP
)

from .tool_selector import (
    generate_production_plan,
    select_optimal_tool_for_shot,
    load_tool_stack_db,
    SOTA_TOOL_RECOMMENDATIONS
)

__all__ = [
    # ALT beat generation
    'generate_alt_beats',
    'validate_alt_beats_timing',
    'calculate_eight_part_timing',
    'BEAT_TEMPLATES',
    
    # Clarifying questions
    'ask_clarifying_questions',
    'apply_clarifications_to_vrd',
    
    # Shot planning
    'generate_shot_list',
    'SHOT_TYPE_MAP',
    
    # Tool selection
    'generate_production_plan',
    'select_optimal_tool_for_shot',
    'load_tool_stack_db',
    'SOTA_TOOL_RECOMMENDATIONS',
]
