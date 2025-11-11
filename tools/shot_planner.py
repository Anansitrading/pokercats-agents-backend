"""
Shot Planning Tools
Converts ALT beats into detailed shot specifications
"""

from datetime import datetime
from models.alt_beat import ALTBeat
from models.shot import (
    Shot, ShotList, ShotComposition, ShotLighting,
    SetRequirements, TechnicalComplexity, StoryboardFrame, AssetSummary
)


# Shot type mapping based on 8-part position (from research)
SHOT_TYPE_MAP = {
    'hook': 'closeup',                    # Grab attention
    'inciting_event': 'medium',           # Establish context
    'first_plot_point': 'medium_wide',    # Show transition
    'first_pinch_point': 'medium_closeup', # Build tension
    'midpoint': 'wide',                   # Transformation moment
    'second_pinch_point': 'closeup',      # Proof/detail
    'third_plot_point': 'medium',         # Resolve
    'climax': 'medium_wide'               # Action
}


def generate_shot_from_beat(
    beat: ALTBeat,
    shot_number: int,
    shot_duration: int,
    shot_index: int = 0
) -> Shot:
    """
    Generate a single shot specification from an ALT beat
    
    Args:
        beat: ALT beat object
        shot_number: Shot sequence number
        shot_duration: Duration for this shot
        shot_index: Index if beat requires multiple shots
        
    Returns:
        Complete Shot object
    """
    position = beat.narrative_function.eight_part_position
    shot_type = SHOT_TYPE_MAP.get(position, 'medium')
    
    # Determine camera movement based on duration
    camera_movement = 'static' if shot_duration < 4 else 'slow_dolly'
    if position in ['midpoint', 'climax']:
        camera_movement = 'dolly' if shot_duration > 5 else 'slow_push'
    
    # Lighting mood based on position
    lighting_mood = 'bright' if position in ['hook', 'climax', 'midpoint'] else 'neutral'
    
    # Composition focal point (alternate for variety)
    focal_point = 'center_right' if shot_number % 2 == 0 else 'center_left'
    if position in ['hook', 'climax']:
        focal_point = 'center'
    
    # Depth of field based on shot type
    dof = 'shallow' if shot_type in ['closeup', 'medium_closeup', 'extreme_closeup'] else 'deep'
    
    shot = Shot(
        shot_id=f'shot_{shot_number:03d}',
        beat_ref=beat.beat_id,
        shot_number=shot_number,
        shot_type=shot_type,
        subject=f'{position.replace("_", " ")} subject',
        camera_angle='eye_level',
        camera_movement=camera_movement,
        duration_seconds=shot_duration,
        frame_rate=24,
        resolution='1080p',
        
        composition=ShotComposition(
            rule_of_thirds=True,
            focal_point=focal_point,
            depth_of_field=dof
        ),
        
        lighting=ShotLighting(
            time_of_day='day',
            mood=lighting_mood,
            key_light='soft_front_right',
            practical_lights=['background_accent'] if lighting_mood == 'bright' else []
        ),
        
        set_requirements=SetRequirements(
            location_type='studio',
            props=[],
            set_dressing='minimal_modern'
        ),
        
        technical_complexity=TechnicalComplexity(
            complexity_score=7 if position in ['midpoint', 'climax'] else 5,
            requires_motion=shot_duration > 5,
            requires_vfx=beat.production_metadata.requires_vfx,
            requires_compositing=False,
            estimated_generation_time_seconds=45 + (shot_duration * 2)
        ),
        
        storyboard_frame=StoryboardFrame(
            description=f'{shot_type.replace("_", " ").title()} shot for {position} beat',
            reference_image_prompt=f'{shot_type} shot, {beat.visual_requirements.lighting}, professional cinematography, {beat.emotional_context.audience_emotion} mood, {beat.visual_requirements.visual_keywords[0]} theme',
            thumbnail_url=None
        )
    )
    
    return shot


def generate_shot_list(alt_beats: list[ALTBeat], mode: str = "hitl") -> ShotList:
    """
    Convert ALT beats into detailed shot list
    
    Implements:
    - Shot type selection based on beat requirements
    - Camera movement planning
    - Lighting design
    - Composition guidelines
    - Technical complexity estimation
    - Storyboard descriptions
    
    Args:
        alt_beats: List of ALT beat objects from ScriptSmith
        mode: 'hitl' or 'yolo'
        
    Returns:
        Complete ShotList object
    """
    shots = []
    shot_number = 1
    
    for beat in alt_beats:
        duration = beat.duration_seconds
        
        # Determine shots needed (1 shot per 5-7 seconds, minimum 1)
        shots_needed = max(1, round(duration / 6))
        
        for shot_idx in range(shots_needed):
            shot_duration = duration // shots_needed
            
            # Handle remainder on last shot
            if shot_idx == shots_needed - 1:
                shot_duration = duration - (shot_duration * (shots_needed - 1))
            
            shot = generate_shot_from_beat(beat, shot_number, shot_duration, shot_idx)
            shots.append(shot)
            shot_number += 1
    
    # Calculate asset summary
    unique_locations = len(set(s.set_requirements.location_type for s in shots))
    unique_shot_types = len(set(s.shot_type for s in shots))
    vfx_shots = sum(1 for s in shots if s.technical_complexity.requires_vfx)
    total_time_minutes = sum(s.technical_complexity.estimated_generation_time_seconds for s in shots) / 60
    
    asset_summary = AssetSummary(
        total_unique_locations=unique_locations,
        total_unique_shot_types=unique_shot_types,
        total_character_shots=len(shots),
        vfx_shots=vfx_shots,
        requires_custom_models=False,
        estimated_total_time_minutes=round(total_time_minutes, 1)
    )
    
    shot_list = ShotList(
        shot_list_id=f'shotlist_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        script_ref='script_ref',  # Will be populated by orchestrator
        mode=mode,
        total_shots=len(shots),
        total_scenes=len(alt_beats),
        shots=shots,
        asset_summary=asset_summary
    )
    
    return shot_list
