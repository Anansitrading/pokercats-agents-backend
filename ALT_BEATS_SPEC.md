# ALT Beats Specification for Multi-Agent Video Production

## Overview

**ALT (Alternative) Beats** are structured narrative units designed for AI-driven video production pipelines. Each beat answers a specific story question and contains complete metadata for automated generation.

## Core Principles

1. **Atomic Units**: Each beat does ONE thing clearly
2. **Question-Answer Framing**: Every beat answers "what does the audience need to know RIGHT NOW?"
3. **Information Density**: Dense, unambiguous, visually actionable
4. **Metadata Rich**: Emotion, camera, lighting, sound specifications  
5. **Hierarchical Organization**: Chronological within acts
6. **Machine Readable**: JSON format for agent consumption

## Beat Structure

```json
{
  "beat_id": "1.3",
  "scene_id": "001",
  "timecode_start": "00:00:10:00",
  "timecode_end": "00:00:15:00",
  "duration_seconds": 5,
  "sequence_order": 3,
  
  "story_question": "What specific problem is the character facing?",
  "story_answer": "Smart home systems are fragmented and failing",
  
  "script": {
    "action": "BATHROOM. Maya adjusts shower. Water goes ICE COLD. She GASPS and jumps back.",
    "dialogue": "Not again!",
    "voiceover": null,
    "on_screen_text": null
  },
  
  "visual_requirements": {
    "shot_type": "medium_closeup",
    "camera_movement": "static",
    "location": "bathroom",
    "lighting": "morning_natural",
    "visual_keywords": ["steam", "shower", "surprise_reaction"],
    "complexity": "medium"
  },
  
  "audio_requirements": {
    "dialogue_present": true,
    "sound_effects": ["water_spray", "gasp"],
    "music_mood": "tense",
    "ambient": "bathroom_echo"
  },
  
  "emotional_context": {
    "character_emotion": "frustrated",
    "audience_emotion": "empathetic",
    "emotional_arc_position": "problem_escalation",
    "intensity": 7
  },
  
  "narrative_function": {
    "beat_type": "problem_demonstration",
    "story_beat_number": 2,
    "eight_part_position": "inciting_event",
    "info_conveyed": "Smart home exists but isn't working cohesively",
    "raises_question": "How bad will it get?",
    "answers_question": "What's wrong with current setup?"
  },
  
  "production_metadata": {
    "estimated_complexity": "medium",
    "requires_vfx": false,
    "requires_custom_assets": false,
    "suggested_tool_category": "image_to_video",
    "reference_images": []
  }
}
```

## Agent Integration

### ScriptSmith → ShotMaster
- ScriptSmith generates beats with complete metadata
- ShotMaster consumes beats to create detailed shot specifications

### ShotMaster → VideoSolver
- ShotMaster produces shot list with technical requirements
- VideoSolver selects optimal AI tools based on shot specs

### Benefits
- **Precise Timing**: Exact duration and timecode per beat
- **Information Clarity**: Each beat's purpose explicitly stated
- **Automation Ready**: Complete metadata for AI consumption
- **Human Readable**: Narrative remains understandable
- **Flexible**: Supports branching and alternative paths
