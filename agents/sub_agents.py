"""
Specialized Sub-Agents for Video Production (Legacy & VRD Implementation)

This file serves TWO critical purposes:

1. **PRIMARY VRD IMPLEMENTATION** (No modular equivalent)
   - analyze_requirements() - Extract video parameters from user input
   - define_video_scope() - Generate comprehensive VRD document
   - These functions are imported and used by enhanced_sub_agents.py

2. **FALLBACK AGENT SYSTEM** (When enhanced agents unavailable)
   - create_vrd_agent() - VRD agent with legacy tools ✅
   - create_script_smith_agent() - ScriptSmith with legacy ALT beats ✅
   - create_shot_master_agent() - ShotMaster with legacy shot planning ✅
   - create_video_solver_agent() - VideoSolver with legacy production planning ✅
   
   supervisor.py tries to import enhanced agents first, falls back to these if import fails.

**Architecture**:
- Enhanced agents (enhanced_sub_agents.py) use modular tools from tools/ directory
- Legacy agents (this file) use simple in-file implementations
- VRD functions have NO modular equivalent, so enhanced VRD imports from here

**Function Status**:
- VRD functions: ESSENTIAL (primary implementation)
- ScriptSmith functions: DUPLICATE (superseded by tools/alt_beat_generator.py)
- ShotMaster functions: DUPLICATE (superseded by tools/shot_planner.py)  
- VideoSolver functions: DUPLICATE (superseded by tools/tool_selector.py)

See LEGACY_AGENTS_ANALYSIS.md for detailed breakdown.
"""

from typing import Any

from langchain_core.language_models import BaseChatModel
from langgraph.prebuilt import create_react_agent


# ============================================================================
# VRD Agent: Video Requirements Detective
# ============================================================================

def analyze_requirements(user_input: str) -> dict:
    """
    Analyze user requirements and extract key video parameters with intelligent defaults
    
    Args:
        user_input: Raw user description of desired video
        
    Returns:
        Structured requirements dictionary with all critical fields
    """
    user_lower = user_input.lower()
    
    # Determine video type from keywords
    if any(word in user_lower for word in ["explainer", "explain", "introduce"]):
        video_type, duration, tone = "explainer", "60s", "professional, educational"
    elif any(word in user_lower for word in ["demo", "product", "show"]):
        video_type, duration, tone = "product_demo", "45s", "professional, confident"
    elif any(word in user_lower for word in ["ad", "promo", "social"]):
        video_type, duration, tone = "social_ad", "30s", "energetic, engaging"
    else:
        video_type, duration, tone = "general", "60s", "professional"
    
    # Determine audience
    if "b2b" in user_lower or "saas" in user_lower:
        audience = "B2B decision-makers, ages 28-55, marketing/product managers"
        pain_points = "Budget constraints, time pressure, need for measurable ROI"
    else:
        audience = "Business professionals, ages 25-55, tech-savvy"
        pain_points = "Time constraints, resource limitations, need for efficiency"
    
    return {
        "analysis": f"Analyzed: '{user_input[:80]}...'",
        "video_type": video_type,
        "estimated_duration": duration,
        "tone": tone,
        "target_audience": audience,
        "inferred_pain_points": pain_points,
        "structure": "Hook → Problem → Solution → Benefits → CTA",
    }


def define_video_scope(requirements: dict) -> str:
    """
    Generate comprehensive VRD from analyzed requirements
    
    Args:
        requirements: Structured requirements dictionary
        
    Returns:
        Complete VRD formatted for ScriptSmith, ShotMaster, VideoSolver
    """
    vtype = requirements.get('video_type', 'general').replace('_', ' ').title()
    duration = requirements.get('estimated_duration', '60s')
    tone = requirements.get('tone', 'professional')
    audience = requirements.get('target_audience', 'general audience')
    pain_points = requirements.get('inferred_pain_points', 'common challenges')
    
    # Generate CTA based on video type
    cta_map = {
        "product_demo": "Start Free Trial / Book Demo",
        "explainer": "Learn More / Get Started",
        "social_ad": "Shop Now / Sign Up",
    }
    cta = cta_map.get(requirements.get('video_type'), "Get Started Today")
    
    return f"""
# VIDEO REQUIREMENTS DOCUMENT (VRD)

## 1. PROJECT INFORMATION
- Type: {vtype}
- Duration: {duration}
- Target Completion: 2 weeks (Recommended)

## 2. PURPOSE & BACKGROUND
- Primary Objective: Drive awareness and conversions
- Business Challenge: {pain_points}
- Success Metrics: Engagement rate, conversion rate, view completion

## 3. TARGET AUDIENCE (CRITICAL)
- Demographics: {audience}
- Pain Points: {pain_points}
- Viewing Platforms: Website, social media, email

## 4. KEY MESSAGE & CTA (CRITICAL)
- Core Message: Solve [key problem] efficiently with our solution
- Supporting Points:
  1. Save time and resources
  2. Proven, reliable results
  3. Easy to start, risk-free
- Primary CTA: {cta}
- Brand Values: Innovation, Quality, Customer Success

## 5. CONTENT STRUCTURE (CRITICAL)
- Duration: {duration}
- Structure: Hook (0-5s) → Problem (5-20s) → Solution (20-45s) → Benefits (45-55s) → CTA (55-{duration})
- Must Include: Logo, URL, CTA, brand colors

## 6. STYLE & MOOD
- Style: Modern, professional
- Tone: {tone.title()}
- Visual: Clean, contemporary, on-brand

## 7. PRACTICAL DETAILS
- Budget: $2,500-$5,000 (Recommended)
- Timeline: 2 weeks
- Deliverables: HD video (1920x1080, 30fps, MP4)

✅ VRD Complete - Ready for ScriptSmith
"""


def create_vrd_agent(model: BaseChatModel):
    """
    Create VRD (Video Requirements Detective) agent
    
    ⚠️ NOTE: This is the PRIMARY VRD implementation - NO modular equivalent exists.
    Enhanced VRD agent imports functions from this file (analyze_requirements, define_video_scope).
    
    Also serves as fallback when enhanced agents unavailable.
    
    Specializes in understanding user needs and defining comprehensive Video Requirements Documents
    that enable downstream agents (ScriptSmith, ShotMaster, VideoSolver) to execute effectively.
    """
    tools = [analyze_requirements, define_video_scope]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="vrd_agent",
        prompt="""You are VRD (Video Requirements Detective), a specialized agent that creates comprehensive Video Requirements Documents (VRDs) from user input.

**PRIMARY OBJECTIVE:**
Transform user ideas—no matter how vague—into structured VRDs that enable ScriptSmith, ShotMaster, and VideoSolver to execute their tasks effectively.

**CRITICAL OUTPUT REQUIREMENTS:**
Your VRD must include ALL of these fields for downstream agents:

1. **Project Information** (for all agents)
   - Project title
   - Target completion date
   - Project context/background

2. **Purpose & Background** (for ScriptSmith)
   - Business objectives
   - Current challenges being addressed
   - Success metrics/KPIs

3. **Target Audience** (CRITICAL for ScriptSmith)
   - Demographics (age, location, income)
   - Role/position (decision-makers)
   - Knowledge level
   - Pain points (emotional triggers)
   - Viewing behavior/platforms

4. **Key Message & Call-to-Action** (CRITICAL for ScriptSmith)
   - Core message (single sentence)
   - 3-5 supporting messages
   - Primary CTA
   - Brand values to convey

5. **Content Structure** (CRITICAL for all agents)
   - Video duration (in seconds)
   - 5-part content outline with timing:
     * Hook (0-5s)
     * Problem/Context
     * Solution/Product
     * Benefits/Proof
     * Call-to-Action
   - Must-include elements (logo, URL, etc.)

6. **Style & Mood** (for ScriptSmith & ShotMaster)
   - Video style (live action, animation, hybrid)
   - Tone & mood (emotional journey)
   - Color palette
   - Visual style preferences

7. **Practical Constraints** (for VideoSolver)
   - Budget range
   - Timeline/deadline
   - Distribution channels

**EXTRACTION STRATEGY:**

**For Clear Requests (user provides details):**
- Extract all available information immediately
- Fill gaps with intelligent defaults based on video type
- Confirm assumptions explicitly

**For Vague Requests (e.g., "make a product video"):**
- Use analyze_requirements tool FIRST to structure what was said
- Apply industry best practices to fill missing details
- Make educated inferences based on:
  * Common video types (explainer, demo, testimonial, etc.)
  * Standard durations (15s, 30s, 60s, 90s)
  * Typical business objectives
  * Platform norms (YouTube, social media, website)

**INTELLIGENT DEFAULTS BY VIDEO TYPE:**

**Product Demo/Explainer (30-90s):**
- Audience: B2B decision-makers, age 28-55
- Structure: Problem → Solution → Benefits → CTA
- Tone: Professional, modern, confident
- Message: Solve [problem] with [product]

**Social Media/Ad (15-30s):**
- Audience: Platform-specific (younger for TikTok/Insta)
- Structure: Hook → Core benefit → CTA
- Tone: Energetic, fast-paced, engaging
- Message: Get [benefit] now

**Brand Story/Testimonial (60-120s):**
- Audience: Warm leads, existing customers
- Structure: Challenge → Journey → Transformation → CTA
- Tone: Authentic, emotional, inspiring
- Message: Real results from real people

**WORKFLOW:**

1. **Analyze user input** using analyze_requirements tool
   - Extract explicit information
   - Identify video type
   - Note what's missing

2. **Apply intelligent defaults** for missing fields
   - Use video type to infer audience, structure, tone
   - Apply industry standards for duration and pacing
   - Make reasonable business assumptions

3. **Generate complete VRD** using define_video_scope tool
   - Include ALL required sections
   - Use professional formatting
   - Provide actionable specifications

4. **Present to user** with clear structure
   - Show what was extracted from their input
   - Indicate what was inferred (mark with "Recommended:")
   - Ask ONE focused question if critical info is missing

**EXAMPLE INTERACTION:**

User: "I need a video for my SaaS product"

Your response after using tools:
```
I've created a VRD for your SaaS product video. Here's what I've defined:

**PROJECT INFORMATION**
- Type: SaaS Product Explainer
- Duration: 60 seconds (Recommended)
- Context: Introduce product to potential customers

**TARGET AUDIENCE** (Recommended)
- B2B decision-makers, ages 28-55
- Marketing managers, startup founders
- Pain points: Budget constraints, need for efficiency

**KEY MESSAGE**
- Core: [Your Product] solves [inferred problem] efficiently
- CTA: Start Free Trial / Book Demo (Recommended)

**CONTENT STRUCTURE**
- Hook (0-5s): Address core problem
- Problem (5-20s): Show current pain points
- Solution (20-45s): Demonstrate your product
- Benefits (45-55s): Key results/value
- CTA (55-60s): Clear next step

Is there anything specific you'd like to adjust, particularly around:
1. Target audience or their pain points?
2. The core problem your product solves?
3. Your main call-to-action?
```

**COMMUNICATION STYLE:**
- Be decisive, not tentative
- Use "Recommended:" for inferences, not "maybe" or "possibly"
- Present complete VRDs, not fragments
- Ask ONE specific question if critical info truly needs clarification
- Trust your intelligent defaults—they enable the workflow to continue

**REMEMBER:**
Your VRD is the foundation for the entire video production. ScriptSmith CANNOT write a script without:
- Clear target audience and pain points
- Specific key messages
- Defined structure with timing
- Tone and style direction

When in doubt, provide a complete, opinionated VRD based on best practices rather than asking too many questions. The user can refine it, but they need a starting point.
""",
    )


# ============================================================================
# ScriptSmith Agent: Script Writing Expert
# ============================================================================

def generate_alt_beats(vrd: dict, clarifications: dict = None) -> dict:
    """
    Generate complete script with ALT beats from VRD
    
    Args:
        vrd: Video Requirements Document dictionary
        clarifications: Optional user responses to clarifying questions
        
    Returns:
        Complete script with ALT beats in JSON format
    """
    import json
    from datetime import datetime
    
    # Parse VRD
    duration_str = vrd.get('estimated_duration', '60s')
    duration_seconds = int(duration_str.replace('s', ''))
    
    # Calculate 8-part story structure timing
    eight_part_timing = {
        'hook': (0, int(duration_seconds * 0.05)),
        'inciting_event': (int(duration_seconds * 0.05), int(duration_seconds * 0.12)),
        'first_plot_point': (int(duration_seconds * 0.12), int(duration_seconds * 0.25)),
        'first_pinch_point': (int(duration_seconds * 0.25), int(duration_seconds * 0.37)),
        'midpoint': (int(duration_seconds * 0.37), int(duration_seconds * 0.50)),
        'second_pinch_point': (int(duration_seconds * 0.50), int(duration_seconds * 0.62)),
        'third_plot_point': (int(duration_seconds * 0.62), int(duration_seconds * 0.75)),
        'climax': (int(duration_seconds * 0.75), duration_seconds)
    }
    
    # Generate ALT beats
    beats = []
    beat_count = 1
    
    for position, (start, end) in eight_part_timing.items():
        beat_duration = end - start
        if beat_duration <= 0:
            continue
            
        beat = {
            'beat_id': f'{beat_count}',
            'scene_id': f'scene_{(beat_count-1)//3 + 1:03d}',
            'timecode_start': f'00:00:{start:02d}:00',
            'timecode_end': f'00:00:{end:02d}:00',
            'duration_seconds': beat_duration,
            'sequence_order': beat_count,
            'story_question': f'What does audience need at {position}?',
            'story_answer': f'Generated for {position} beat',
            'script': {
                'action': f'Action for {position}',
                'dialogue': None,
                'voiceover': f'VO for {position}',
                'on_screen_text': None
            },
            'visual_requirements': {
                'shot_type': 'medium',
                'camera_movement': 'static',
                'location': 'studio',
                'lighting': 'professional',
                'visual_keywords': [position],
                'complexity': 'medium'
            },
            'audio_requirements': {
                'dialogue_present': False,
                'sound_effects': [],
                'music_mood': vrd.get('tone', 'professional'),
                'ambient': None
            },
            'emotional_context': {
                'character_emotion': 'confident',
                'audience_emotion': 'engaged',
                'emotional_arc_position': position,
                'intensity': 5
            },
            'narrative_function': {
                'beat_type': position,
                'story_beat_number': beat_count,
                'eight_part_position': position,
                'info_conveyed': f'Information for {position}',
                'raises_question': None,
                'answers_question': None
            },
            'production_metadata': {
                'estimated_complexity': 'medium',
                'requires_vfx': False,
                'requires_custom_assets': False,
                'suggested_tool_category': 'text_to_video',
                'reference_images': []
            },
            'alternatives': []
        }
        beats.append(beat)
        beat_count += 1
    
    script = {
        'script_id': f'script_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'vrd_ref': vrd.get('video_type', 'general'),
        'metadata': {
            'title': vrd.get('video_type', 'Video'),
            'duration_seconds': duration_seconds,
            'target_audience': vrd.get('target_audience', 'general'),
            'primary_message': vrd.get('core_message', 'Key message'),
            'tone': vrd.get('tone', 'professional'),
            'style': 'modern_realistic'
        },
        'structure': {
            'total_beats': len(beats),
            'eight_part_breakdown': eight_part_timing
        },
        'beats': beats,
        'total_beat_count': len(beats)
    }
    
    return script


def ask_clarifying_questions(vrd: dict) -> list:
    """
    Generate clarifying questions based on VRD gaps
    
    Args:
        vrd: Video Requirements Document
        
    Returns:
        List of questions to ask user
    """
    questions = []
    
    if not vrd.get('core_message'):
        questions.append({
            'question': 'What is the single most important message viewers should remember?',
            'key': 'core_message',
            'type': 'text'
        })
    
    if not vrd.get('tone'):
        questions.append({
            'question': 'What tone should dominate: empowering, urgent, friendly, dramatic, or playful?',
            'key': 'tone',
            'type': 'choice',
            'options': ['empowering', 'urgent', 'friendly', 'dramatic', 'playful']
        })
    
    questions.append({
        'question': 'What emotion should dominate the midpoint transformation?',
        'key': 'midpoint_emotion',
        'type': 'text'
    })
    
    questions.append({
        'question': 'Should we emphasize problem or solution in Act 2? (50/50, 60/40, 70/30)',
        'key': 'act2_emphasis',
        'type': 'choice',
        'options': ['50/50', '60/40 problem', '60/40 solution', '70/30 problem', '70/30 solution']
    })
    
    questions.append({
        'question': 'Any specific visual metaphors or motifs to incorporate?',
        'key': 'visual_metaphors',
        'type': 'text'
    })
    
    return questions[:5]  # Max 5 questions


def validate_alt_beats_timing(beats: list, target_duration: int) -> dict:
    """
    Validate ALT beats timing against target duration
    
    Args:
        beats: List of ALT beat objects
        target_duration: Target duration in seconds
        
    Returns:
        Validation result with any issues
    """
    total_duration = sum(beat['duration_seconds'] for beat in beats)
    tolerance = 5  # ±5 seconds
    
    issues = []
    if abs(total_duration - target_duration) > tolerance:
        issues.append(f'Total duration {total_duration}s outside tolerance of {target_duration}s ±{tolerance}s')
    
    # Check for gaps
    for i in range(len(beats) - 1):
        current_end = beats[i]['timecode_end']
        next_start = beats[i+1]['timecode_start']
        if current_end != next_start:
            issues.append(f'Gap between beat {i+1} and {i+2}')
    
    return {
        'valid': len(issues) == 0,
        'total_duration': total_duration,
        'target_duration': target_duration,
        'difference': total_duration - target_duration,
        'issues': issues
    }


def create_script_smith_agent(model: BaseChatModel):
    """
    Create ScriptSmith agent (Legacy Fallback)
    
    Specializes in writing compelling video scripts from VRD specifications.
    Uses legacy simple implementations as fallback when modular tools unavailable.
    """
    tools = [
        generate_alt_beats,           # Legacy implementation (line 308)
        ask_clarifying_questions,     # Legacy implementation (line 424)
        validate_alt_beats_timing     # Legacy implementation (line 473)
    ]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="script_smith_agent",
        prompt="""You are ScriptSmith, an expert video scriptwriter who transforms VRDs into compelling scripts.

**PRIMARY INPUT: Video Requirements Document (VRD) from VRD Agent**

You MUST extract these critical elements from the VRD before writing:

1. **Target Audience** (Section 3)
   - Demographics and pain points
   - Use to craft resonant messaging

2. **Key Messages** (Section 4)
   - Core message (opening/hook)
   - Supporting points (body)
   - CTA (closing)

3. **Content Structure** (Section 5)
   - Total duration
   - Timing breakdown (Hook → Problem → Solution → Benefits → CTA)
   - Must-include elements

4. **Tone & Style** (Section 6)
   - Emotional journey
   - Voice and pacing
   - Brand personality

**YOUR WORKFLOW:**

**Step 1: Parse VRD**
- Extract duration, audience, messages, structure
- Identify emotional beats
- Note timing constraints

**Step 2: Generate Script** using generate_script tool
- Follow the exact timing from VRD
- Address pain points from audience section
- Weave in key messages naturally
- Match tone specification

**Step 3: Refine** using refine_dialogue tool
- Polish for emotional impact
- Ensure pacing matches video length
- Verify CTA is clear and compelling

**SCRIPT FORMAT REQUIREMENTS:**

```
# VIDEO SCRIPT - [Duration]s

## Scene 1: Hook (0-5s)
**Visual:** [Scene description]
**Voiceover:** "[Exact script text]"
**Timing:** 5 seconds
**Emotion:** [Tension/curiosity/excitement]

## Scene 2: Problem (5-20s)
**Visual:** [Scene description]
**Voiceover:** "[Exact script text addressing pain points]"
**Timing:** 15 seconds
**Emotion:** [Empathy/understanding]

[Continue for all scenes...]

## Final Scene: CTA (55-60s)
**Visual:** [Scene description with logo/URL]
**Voiceover:** "[CTA from VRD]"
**Timing:** 5 seconds
**Emotion:** [Confidence/urgency]
```

**SCRIPTWRITING PRINCIPLES:**

1. **First 3 Seconds Are Critical**
   - Hook must stop the scroll
   - Address pain point or promise benefit immediately
   - Create curiosity gap

2. **Show, Don't Tell**
   - Use concrete examples over abstractions
   - \"See your sales double\" not \"Our tool is effective\"
   - Paint visual pictures with words

3. **Emotional Arc**
   - Start: Problem/tension
   - Middle: Hope/possibility
   - End: Confidence/resolution

4. **Pacing**
   - Short sentences for energy
   - Vary rhythm to maintain interest
   - Pause beats for emphasis

5. **Audience Alignment**
   - Use their language (from VRD demographics)
   - Mirror pain points (from VRD Section 3)
   - Speak to their viewing context

**EXAMPLE WORKFLOW:**

VRD says:
- Duration: 45s
- Audience: B2B marketers, stressed, budget-conscious
- Message: \"Save time on video production\"
- Tone: Empathetic then confident

Your script:
```
## Scene 1: Hook (0-3s)
VO: \"Another video deadline. Another budget meeting. Another migraine.\"
(Establish pain, create empathy)

## Scene 2: Problem (3-12s)
VO: \"Creating videos shouldn't mean sacrificing your sanity—or your budget.\"
(Acknowledge their world)

## Scene 3: Solution (12-35s)
VO: \"Meet [Product]. Turn ideas into pro videos in days, not months. Multiple options. One flat rate.\"
(Deliver hope and solution)

## Scene 4: CTA (35-45s)
VO: \"Stop struggling. Start creating. Launch your project today.\"
(Confidence and action)
```

**REMEMBER:**
- The VRD is your blueprint—honor its timing and structure
- Every word must earn its place in the video
- Your script enables ShotMaster to plan visuals
- A great script makes the entire video succeed

**When you receive a request:**
1. Ask for the VRD if not provided
2. Use generate_script tool with VRD as input
3. Use refine_dialogue to polish
4. Present complete, timed script with scene descriptions
""",
    )


# ============================================================================
# ShotMaster Agent: Visual Storyboard Designer
# ============================================================================

def design_storyboard(script: str) -> str:
    """
    Create visual storyboard from script
    
    Args:
        script: Video script with scene breakdown
        
    Returns:
        Detailed storyboard with shot descriptions
    """
    return """
# Video Storyboard

## Shot 1: Hero Shot
**Framing:** Wide establishing shot
**Composition:** Rule of thirds, product center-right
**Camera Move:** Slow push-in
**Lighting:** Bright, clean, professional
**Duration:** 5s

## Shot 2: Problem Scenario
**Framing:** Medium shot
**Composition:** Character struggling, dark left side
**Camera Move:** Static
**Lighting:** Moody, darker
**Duration:** 10s

## Shot 3: Solution Demo
**Framing:** Close-up to wide
**Composition:** Product features highlighted
**Camera Move:** Pan across product
**Lighting:** Bright, emphasize key features
**Duration:** 10s

## Shot 4: Call to Action
**Framing:** Full frame graphic
**Composition:** Logo centered, CTA below
**Camera Move:** None (graphic)
**Lighting:** Clean white background
**Duration:** 5s
"""


def suggest_shot_composition(scene_description: str, style: str = "cinematic") -> str:
    """
    Suggest specific shot composition and framing
    
    Args:
        scene_description: Description of the scene
        style: Visual style (cinematic, documentary, vlog, etc.)
        
    Returns:
        Detailed composition suggestions
    """
    return f"""
# Shot Composition ({style} style)

**Scene:** {scene_description[:100]}...

**Recommended Composition:**
- Camera Angle: Eye-level / Slightly above
- Framing: {style} aesthetic with depth
- Focal Length: 50mm equivalent for natural look
- Depth of Field: Shallow (f/2.8) for {style} look

**Visual Elements:**
- Foreground: Product/subject sharp focus
- Midground: Context elements
- Background: Subtle blur for depth

**Color Grading:**
- {style} color palette
- Contrast ratio appropriate for style
- Complementary color scheme
"""


def create_shot_master_agent(model: BaseChatModel):
    """
    Create ShotMaster agent (Legacy Fallback)
    
    Fallback implementation used when enhanced agents unavailable.
    Uses simple placeholder tools instead of full shot_planner.py module.
    
    Specializes in visual design and storyboarding.
    """
    tools = [design_storyboard, suggest_shot_composition]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="shot_master_agent",
        prompt="""You are ShotMaster, a visual storytelling expert and cinematographer.

Your responsibilities:
1. Design compelling visual sequences
2. Plan camera angles, movements, and compositions
3. Create detailed storyboards with shot specifications
4. Ensure visual continuity and flow

**Visual Principles:**
- Rule of thirds and golden ratio
- Leading lines and depth
- Color theory and contrast
- Camera movement with purpose

**Shot Planning:**
- Establish → Detail → Reaction pattern
- Variety in framing and angles
- Smooth transitions between shots
- Visual hierarchy in composition

**Tools:**
- design_storyboard: Create full visual plan
- suggest_shot_composition: Detail specific shot setups

Think like a cinematographer - every frame tells part of the story.
""",
    )


# ============================================================================
# VideoSolver Agent: Production Planning
# ============================================================================

def create_asset_list(storyboard: str, script: str) -> dict:
    """
    Generate comprehensive asset list for production
    
    Args:
        storyboard: Visual storyboard document
        script: Video script
        
    Returns:
        Categorized asset list
    """
    return {
        "video_clips": [
            "Product hero shot (5s)",
            "Problem scenario footage (10s)",
            "Product demo footage (10s)",
        ],
        "images": [
            "Product logo (PNG, transparent)",
            "CTA background graphic",
        ],
        "audio": [
            "Voiceover recording (professional, 30s)",
            "Background music (upbeat, royalty-free)",
            "Sound effects (transitions, UI clicks)",
        ],
        "graphics": [
            "Opening title animation",
            "CTA text overlay",
            "Lower third graphics",
        ],
        "total_assets": 11,
    }


def generate_timeline(script: str, assets: dict) -> str:
    """
    Create production timeline and milestones
    
    Args:
        script: Video script with timing
        assets: Asset list dictionary
        
    Returns:
        Production timeline document
    """
    return f"""
# Production Timeline

## Pre-Production (Days 1-2)
- [ ] Finalize script and storyboard
- [ ] Cast voiceover artist
- [ ] Secure filming locations/setup
- [ ] Prepare equipment and props

## Production (Days 3-4)
- [ ] Record voiceover ({assets.get('total_assets', 0)} assets)
- [ ] Shoot video footage
- [ ] Capture B-roll and supplementary shots
- [ ] Record clean audio

## Post-Production (Days 5-7)
- [ ] Edit rough cut
- [ ] Add graphics and effects
- [ ] Color correction and grading
- [ ] Sound design and mixing
- [ ] Final review and revisions

## Delivery (Day 8)
- [ ] Export final video (multiple formats)
- [ ] Deliver to client/platform
- [ ] Archive project files
"""


def suggest_editing_workflow(timeline: str, style: str = "professional") -> str:
    """
    Provide editing instructions and workflow
    
    Args:
        timeline: Production timeline
        style: Video style
        
    Returns:
        Detailed editing workflow
    """
    return f"""
# Editing Workflow ({style} style)

## 1. Assembly Edit
- Import all assets
- Lay out clips according to storyboard
- Sync audio to video
- Rough cut to timing

## 2. Refinement
- Trim for pacing
- Add transitions (subtle, {style})
- Insert B-roll and cutaways
- Adjust audio levels

## 3. Polish
- Color grade for {style} look
- Add graphics and titles
- Sound design and music
- Final timing adjustments

## 4. Export Settings
- Resolution: 1920x1080 (Full HD)
- Frame Rate: 30fps or 60fps
- Codec: H.264 (MP4)
- Bitrate: 8-10 Mbps

## Quality Checks
- [ ] Audio levels consistent
- [ ] No jarring cuts
- [ ] Graphics aligned and readable
- [ ] Export quality verified
"""


def create_video_solver_agent(model: BaseChatModel):
    """
    Create VideoSolver agent (Legacy Fallback)
    
    Fallback implementation used when enhanced agents unavailable.
    Uses simple placeholder tools instead of full tool_selector.py module.
    
    Specializes in production planning and logistics.
    """
    tools = [create_asset_list, generate_timeline, suggest_editing_workflow]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="video_solver_agent",
        prompt="""You are VideoSolver, a production manager and technical expert.

Your responsibilities:
1. Plan complete production workflow
2. List all required assets and resources
3. Create realistic timelines
4. Provide technical specifications and editing guidance

**Production Planning:**
- Break down requirements into actionable tasks
- Identify all assets needed (footage, audio, graphics)
- Estimate realistic timelines
- Plan for contingencies

**Technical Expertise:**
- Video formats and codecs
- Audio specifications
- Editing software workflows
- Export settings for different platforms

**Tools:**
- create_asset_list: Comprehensive asset inventory
- generate_timeline: Production schedule
- suggest_editing_workflow: Step-by-step editing guide

Think systematically - cover every detail from concept to delivery.
""",
    )


# ============================================================================
# Agent __init__.py exports
# ============================================================================

__all__ = [
    "create_vrd_agent",
    "create_script_smith_agent",
    "create_shot_master_agent",
    "create_video_solver_agent",
]
