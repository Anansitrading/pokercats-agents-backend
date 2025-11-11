"""
Clarifying Questions Tool
Generates targeted questions based on VRD gaps and mode
"""

from typing import Literal


def ask_clarifying_questions(vrd: dict, mode: Literal["hitl", "yolo"] = "hitl") -> list[dict]:
    """
    Generate smart clarifying questions based on VRD and mode
    
    In YOLO mode: Returns empty list (use defaults)
    In HITL mode: Returns up to 5 targeted questions
    
    Args:
        vrd: Video Requirements Document
        mode: 'hitl' or 'yolo'
        
    Returns:
        List of question dictionaries with keys:
        - question: The question text
        - key: VRD key to update
        - type: 'text' or 'choice'
        - options: List of choices (if type='choice')
        - priority: 'high', 'medium', or 'low'
        - default: Default value (optional)
    """
    if mode == "yolo":
        return []
    
    questions = []
    
    # Priority 1: Core message (critical)
    if not vrd.get('core_message'):
        questions.append({
            'question': 'What is the ONE key message viewers should remember after watching?',
            'key': 'core_message',
            'type': 'text',
            'priority': 'high',
            'hint': 'Example: "Our platform makes video creation 10x faster"'
        })
    
    # Priority 2: Tone (critical for scriptwriting)
    if not vrd.get('tone'):
        questions.append({
            'question': 'What tone should the video have?',
            'key': 'tone',
            'type': 'choice',
            'options': ['empowering', 'urgent', 'friendly', 'dramatic', 'playful', 'professional'],
            'priority': 'high',
            'default': 'professional'
        })
    
    # Priority 3: Midpoint emotion (affects narrative arc)
    questions.append({
        'question': 'What emotion should the viewer feel at the midpoint (50% mark)?',
        'key': 'midpoint_emotion',
        'type': 'choice',
        'options': ['hopeful', 'inspired', 'curious', 'confident', 'relieved', 'excited'],
        'priority': 'medium',
        'default': 'hopeful',
        'hint': 'This is the "transformation moment" where understanding clicks'
    })
    
    # Priority 4: Act 2 emphasis (structural balance)
    questions.append({
        'question': 'In Act 2, should we emphasize the problem or the solution more?',
        'key': 'act2_emphasis',
        'type': 'choice',
        'options': [
            '50/50 - Equal balance',
            '60/40 problem - More pain points',
            '60/40 solution - More benefits',
            '70/30 problem - Heavy on challenges',
            '70/30 solution - Heavy on features'
        ],
        'priority': 'medium',
        'default': '50/50 - Equal balance',
        'hint': 'Problem-heavy works for aware audiences; solution-heavy for unaware'
    })
    
    # Priority 5: Visual metaphors (creative direction)
    questions.append({
        'question': 'Any specific visual metaphors, motifs, or recurring imagery to incorporate?',
        'key': 'visual_metaphors',
        'type': 'text',
        'priority': 'low',
        'optional': True,
        'hint': 'Examples: "journey", "transformation", "building blocks", "unlock", etc.'
    })
    
    # Priority 6: Call-to-action specificity
    if not vrd.get('cta'):
        questions.append({
            'question': 'What specific action should viewers take after watching?',
            'key': 'cta',
            'type': 'choice',
            'options': [
                'Visit website',
                'Start free trial',
                'Book a demo',
                'Download app',
                'Sign up',
                'Contact sales',
                'Learn more'
            ],
            'priority': 'high',
            'hint': 'Be specific - vague CTAs reduce conversion'
        })
    
    # Sort by priority and limit to 5
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    questions.sort(key=lambda q: priority_order.get(q['priority'], 3))
    
    return questions[:5]


def apply_clarifications_to_vrd(vrd: dict, clarifications: dict) -> dict:
    """
    Apply user clarifications to VRD
    
    Args:
        vrd: Original VRD
        clarifications: User responses to questions
        
    Returns:
        Updated VRD with clarifications merged
    """
    updated_vrd = vrd.copy()
    updated_vrd.update(clarifications)
    return updated_vrd
