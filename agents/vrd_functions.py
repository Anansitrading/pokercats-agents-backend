"""
VRD (Video Requirements Detective) Core Functions
Essential requirement analysis - no modular equivalent exists

These functions are the PRIMARY implementation used by enhanced agents.
They analyze user input and generate comprehensive Video Requirements Documents.
"""


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


__all__ = [
    "analyze_requirements",
    "define_video_scope",
]
