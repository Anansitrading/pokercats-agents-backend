"""
ALT Beat Generation Tools
Core logic for generating ALT beats from VRD
"""

from datetime import datetime
from models.alt_beat import (
    ALTBeat, Script, ScriptMetadata, ScriptStructure,
    ScriptContent, VisualRequirements, AudioRequirements,
    EmotionalContext, NarrativeFunction, ProductionMetadata
)


# 8-part story structure beat templates (from research)
BEAT_TEMPLATES = {
    'hook': {
        'story_question': 'Why should the viewer keep watching?',
        'story_answer': 'Create immediate engagement through problem recognition',
        'shot_types': ['closeup', 'medium_closeup'],
        'camera_movement': 'static',
        'lighting': 'professional_bright',
        'intensity': 7,
        'complexity': 'high'
    },
    'inciting_event': {
        'story_question': 'What problem does the viewer face?',
        'story_answer': 'Establish the core challenge and pain point',
        'shot_types': ['medium', 'medium_wide'],
        'camera_movement': 'slow_push',
        'lighting': 'professional_neutral',
        'intensity': 6,
        'complexity': 'medium'
    },
    'first_plot_point': {
        'story_question': 'What solution exists?',
        'story_answer': 'Introduce the product/service as the answer',
        'shot_types': ['wide', 'medium'],
        'camera_movement': 'dolly',
        'lighting': 'professional_bright',
        'intensity': 5,
        'complexity': 'medium'
    },
    'first_pinch_point': {
        'story_question': 'What obstacles remain?',
        'story_answer': 'Show challenges that still need addressing',
        'shot_types': ['closeup', 'medium'],
        'camera_movement': 'static',
        'lighting': 'professional_neutral',
        'intensity': 6,
        'complexity': 'medium'
    },
    'midpoint': {
        'story_question': 'How does the solution transform the situation?',
        'story_answer': 'Demonstrate the key breakthrough or insight',
        'shot_types': ['medium', 'wide'],
        'camera_movement': 'slow_push',
        'lighting': 'professional_bright',
        'intensity': 8,
        'complexity': 'high'
    },
    'second_pinch_point': {
        'story_question': 'What proves this works?',
        'story_answer': 'Present evidence and social proof',
        'shot_types': ['closeup', 'medium_closeup'],
        'camera_movement': 'static',
        'lighting': 'professional_bright',
        'intensity': 7,
        'complexity': 'medium'
    },
    'third_plot_point': {
        'story_question': 'What\'s the final hurdle?',
        'story_answer': 'Address last objections or concerns',
        'shot_types': ['medium', 'medium_wide'],
        'camera_movement': 'slow_push',
        'lighting': 'professional_neutral',
        'intensity': 6,
        'complexity': 'medium'
    },
    'climax': {
        'story_question': 'What action should the viewer take?',
        'story_answer': 'Clear, compelling call-to-action',
        'shot_types': ['medium', 'wide'],
        'camera_movement': 'dolly',
        'lighting': 'professional_bright',
        'intensity': 9,
        'complexity': 'high'
    }
}


def calculate_eight_part_timing(duration_seconds: int) -> dict[str, tuple[int, int]]:
    """
    Calculate 8-part story structure timing breakdown
    
    Based on research: Hook (5%) → Inciting (12%) → 1st Plot (25%) → 
    1st Pinch (37%) → Midpoint (50%) → 2nd Pinch (62%) → 3rd Plot (75%) → Climax (100%)
    
    Args:
        duration_seconds: Total video duration
        
    Returns:
        Dictionary mapping beat position to (start, end) seconds
    """
    return {
        'hook': (0, max(3, int(duration_seconds * 0.05))),
        'inciting_event': (int(duration_seconds * 0.05), int(duration_seconds * 0.12)),
        'first_plot_point': (int(duration_seconds * 0.12), int(duration_seconds * 0.25)),
        'first_pinch_point': (int(duration_seconds * 0.25), int(duration_seconds * 0.37)),
        'midpoint': (int(duration_seconds * 0.37), int(duration_seconds * 0.50)),
        'second_pinch_point': (int(duration_seconds * 0.50), int(duration_seconds * 0.62)),
        'third_plot_point': (int(duration_seconds * 0.62), int(duration_seconds * 0.75)),
        'climax': (int(duration_seconds * 0.75), duration_seconds)
    }


def generate_alt_beat(
    position: str,
    start: int,
    end: int,
    beat_number: int,
    vrd: dict,
    clarifications: dict = None
) -> ALTBeat:
    """
    Generate a single ALT beat with complete metadata
    
    Args:
        position: 8-part position (hook, inciting_event, etc.)
        start: Start time in seconds
        end: End time in seconds
        beat_number: Beat sequence number
        vrd: Video Requirements Document
        clarifications: Optional user clarifications
        
    Returns:
        Complete ALT beat object
    """
    template = BEAT_TEMPLATES.get(position, BEAT_TEMPLATES['hook'])
    duration = end - start
    
    # Extract VRD info
    tone = clarifications.get('tone') if clarifications else vrd.get('tone', 'professional')
    video_type = vrd.get('video_type', 'explainer')
    
    # Build beat
    beat = ALTBeat(
        beat_id=f'{beat_number}.0',
        scene_id=f'scene_{(beat_number-1)//3 + 1:03d}',
        sequence_order=beat_number,
        
        timecode_start=f'00:00:{start:02d}:00',
        timecode_end=f'00:00:{end:02d}:00',
        duration_seconds=duration,
        
        story_question=template['story_question'],
        story_answer=template['story_answer'],
        
        script=ScriptContent(
            action=f'{position.replace("_", " ").title()} action sequence',
            dialogue=None,
            voiceover=f'Voiceover for {position} ({duration}s)',
            on_screen_text=None
        ),
        
        visual_requirements=VisualRequirements(
            shot_type=template['shot_types'][0],
            camera_movement=template['camera_movement'],
            location='studio',
            lighting=template['lighting'],
            visual_keywords=[position, video_type],
            complexity=template['complexity']
        ),
        
        audio_requirements=AudioRequirements(
            dialogue_present=False,
            sound_effects=['transition'] if beat_number > 1 else [],
            music_mood=tone,
            ambient='professional_studio'
        ),
        
        emotional_context=EmotionalContext(
            character_emotion='confident' if position in ['climax', 'midpoint'] else 'curious',
            audience_emotion='engaged' if position == 'hook' else 'interested',
            emotional_arc_position=position,
            intensity=template['intensity']
        ),
        
        narrative_function=NarrativeFunction(
            beat_type=position,
            story_beat_number=beat_number,
            eight_part_position=position,
            info_conveyed=template['story_answer'],
            raises_question=template['story_question'],
            answers_question=template['story_answer'] if beat_number > 1 else None
        ),
        
        production_metadata=ProductionMetadata(
            estimated_complexity=template['complexity'],
            requires_vfx=position in ['hook', 'midpoint', 'climax'],
            requires_custom_assets=True,
            suggested_tool_category='text_to_video' if duration > 5 else 'image_to_video',
            reference_images=[]
        ),
        
        alternatives=[]
    )
    
    return beat


def generate_alt_beats(vrd: dict, clarifications: dict = None, mode: str = "hitl") -> Script:
    """
    Generate complete script with ALT beats from VRD
    
    Main entry point for ALT beat generation
    
    Args:
        vrd: Video Requirements Document
        clarifications: Optional user responses to questions
        mode: 'hitl' (human-in-the-loop) or 'yolo' (full auto)
        
    Returns:
        Complete Script object with ALT beats
    """
    # Parse VRD
    duration_str = vrd.get('estimated_duration', '60s')
    duration_seconds = int(duration_str.replace('s', ''))
    video_type = vrd.get('video_type', 'explainer')
    tone = clarifications.get('tone') if clarifications else vrd.get('tone', 'professional')
    
    # Calculate 8-part timing
    eight_part_timing = calculate_eight_part_timing(duration_seconds)
    
    # Generate beats
    beats = []
    beat_count = 1
    
    for position, (start, end) in eight_part_timing.items():
        beat_duration = end - start
        if beat_duration <= 0:
            continue
        
        beat = generate_alt_beat(position, start, end, beat_count, vrd, clarifications)
        beats.append(beat)
        beat_count += 1
    
    # Build script structure
    structure = ScriptStructure(
        total_beats=len(beats),
        eight_part_breakdown=eight_part_timing,
        act_1_beats=[b.beat_id for b in beats if b.narrative_function.eight_part_position in ['hook', 'inciting_event', 'first_plot_point']],
        act_2_beats=[b.beat_id for b in beats if b.narrative_function.eight_part_position in ['first_pinch_point', 'midpoint', 'second_pinch_point']],
        act_3_beats=[b.beat_id for b in beats if b.narrative_function.eight_part_position in ['third_plot_point', 'climax']]
    )
    
    # Build metadata
    metadata = ScriptMetadata(
        title=vrd.get('project_name', f'{video_type.title()} Video'),
        duration_seconds=duration_seconds,
        target_audience=vrd.get('target_audience', 'general'),
        primary_message=vrd.get('core_message', 'Key message'),
        tone=tone,
        style='modern_realistic'
    )
    
    # Assemble script
    script = Script(
        script_id=f'script_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        vrd_ref=video_type,
        mode=mode,
        metadata=metadata,
        structure=structure,
        beats=beats,
        total_beat_count=len(beats),
        narrative_summary=f'{video_type} video following 8-part structure with {len(beats)} beats'
    )
    
    return script


def validate_alt_beats_timing(beats: list[ALTBeat], target_duration: int) -> dict:
    """
    Validate ALT beats timing against target duration
    
    Args:
        beats: List of ALT beat objects
        target_duration: Target duration in seconds
        
    Returns:
        Validation result with any issues
    """
    total_duration = sum(beat.duration_seconds for beat in beats)
    tolerance = 5  # ±5 seconds
    
    issues = []
    if abs(total_duration - target_duration) > tolerance:
        issues.append(f'Total duration {total_duration}s outside tolerance of {target_duration}s ±{tolerance}s')
    
    # Check for gaps
    for i in range(len(beats) - 1):
        current_end = beats[i].timecode_end
        next_start = beats[i+1].timecode_start
        if current_end != next_start:
            issues.append(f'Gap between beat {i+1} and {i+2}')
    
    return {
        'valid': len(issues) == 0,
        'total_duration': total_duration,
        'target_duration': target_duration,
        'difference': total_duration - target_duration,
        'issues': issues
    }
