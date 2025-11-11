# VRD Agent Optimization Summary

## Overview
Optimized the VRD (Video Requirements Detective) agent to generate comprehensive, structured outputs that enable ScriptSmith (and other downstream agents) to execute effectively.

## Key Changes

### 1. **Enhanced Agent Prompt** (`sub_agents.py` line 73-233)

**From:** Conversational, question-heavy approach designed for Gemini Live
**To:** Structured, output-focused approach for LangGraph multi-agent workflow

**Critical Improvements:**
- **Clear Output Requirements**: Defined exactly what fields must be in every VRD
- **Intelligent Defaults**: Added video-type-specific defaults (explainer, demo, ad, etc.)
- **Downstream Agent Focus**: Explicitly marked which sections each agent needs
- **Decisiveness Over Questions**: Instructs agent to make informed decisions rather than endless questioning

### 2. **Improved Tools**

#### `analyze_requirements()` (lines 16-54)
**Enhanced with:**
- Keyword-based video type detection (explainer, demo, ad, etc.)
- Automatic duration assignment based on video type
- Intelligent audience inference (B2B, consumer, etc.)
- Pain point mapping
- Structured output dictionary

**Example:**
```python
"I need a SaaS explainer" →
{
  "video_type": "explainer",
  "estimated_duration": "60s",
  "tone": "professional, educational",
  "target_audience": "B2B decision-makers, ages 28-55",
  "inferred_pain_points": "Budget constraints, time pressure"
}
```

#### `define_video_scope()` (lines 57-124)
**Enhanced with:**
- Complete 7-section VRD structure
- CTA mapping by video type
- Timing breakdowns based on duration
- Clear markers for critical sections ("CRITICAL FOR SCRIPTSMITH")
- Ready-to-consume format for downstream agents

**Output Structure:**
```markdown
# VIDEO REQUIREMENTS DOCUMENT (VRD)

## 1. PROJECT INFORMATION
## 2. PURPOSE & BACKGROUND
## 3. TARGET AUDIENCE (CRITICAL)
## 4. KEY MESSAGE & CTA (CRITICAL)
## 5. CONTENT STRUCTURE (CRITICAL)
## 6. STYLE & MOOD
## 7. PRACTICAL DETAILS

✅ VRD Complete - Ready for ScriptSmith
```

### 3. **ScriptSmith Integration** (lines 375-522)

**Optimized ScriptSmith to:**
- Explicitly expect VRD as input
- Parse specific VRD sections (3, 4, 5, 6)
- Follow VRD timing exactly
- Match tone and audience specifications
- Generate production-ready scripts with scene-by-scene breakdowns

**Script Format:**
```markdown
## Scene X: [Name] (XX-XXs)
**Visual:** [Description]
**Voiceover:** "[Exact script]"
**Timing:** X seconds
**Emotion:** [Emotion/tone]
```

## Critical Design Decisions

### 1. **Intelligent Defaults Over Questions**
- **Problem**: Original prompt was too conversational, asking many questions
- **Solution**: Agent makes intelligent inferences based on video type
- **Benefit**: Workflow continues even with vague user input

### 2. **Structured Output Format**
- **Problem**: Unstructured VRDs hard for downstream agents to parse
- **Solution**: Consistent 7-section format with marked critical sections
- **Benefit**: ScriptSmith knows exactly where to find needed information

### 3. **Video-Type Classification**
- **Problem**: Each video type has different norms (duration, tone, structure)
- **Solution**: Keyword detection → type classification → type-specific defaults
- **Types Supported**:
  - Explainer (60s, educational, structured)
  - Product Demo (45s, confident, benefit-focused)
  - Social Ad (30s, energetic, hook-heavy)
  - Testimonial (90s, authentic, story-driven)
  - General (60s, professional, flexible)

### 4. **Explicit Agent Handoffs**
- **Problem**: Unclear what each agent needs from VRD
- **Solution**: Marked sections with "(CRITICAL FOR SCRIPTSMITH)" labels
- **Benefit**: Clear data contracts between agents

## Workflow Example

### Input
```
User: "I need a video for my SaaS product"
```

### VRD Agent Processing
1. **analyze_requirements()** detects:
   - Type: product_demo (keyword: "product")
   - Audience: B2B (keyword: "SaaS")
   - Duration: 45s (product demo default)
   - Tone: professional, confident

2. **define_video_scope()** generates:
   - Complete 7-section VRD
   - B2B pain points
   - Product demo structure
   - Appropriate CTA

### Output to ScriptSmith
```markdown
## 3. TARGET AUDIENCE (CRITICAL)
- Demographics: B2B decision-makers, ages 28-55
- Pain Points: Budget constraints, time pressure, need for ROI

## 4. KEY MESSAGE & CTA (CRITICAL)
- Core: Solve [key problem] efficiently
- CTA: Start Free Trial / Book Demo

## 5. CONTENT STRUCTURE (CRITICAL)
- Duration: 45s
- Structure: Hook (0-5s) → Problem (5-15s) → Solution (15-35s) → CTA (35-45s)
```

### ScriptSmith Execution
1. Parses VRD sections 3, 4, 5, 6
2. Generates scene-by-scene script matching:
   - Exact timing from Section 5
   - Pain points from Section 3
   - Messages from Section 4
   - Tone from Section 6
3. Outputs production-ready script

## Testing Recommendations

### Test Case 1: Vague Input
```bash
Input: "I need a video"
Expected: Complete VRD with general video type, 60s duration, professional tone
```

### Test Case 2: Specific Input
```bash
Input: "Create a 30-second social media ad for my e-commerce store"
Expected: Social ad VRD, 30s, energetic tone, consumer audience
```

### Test Case 3: B2B SaaS
```bash
Input: "Explainer video for my project management SaaS"
Expected: Explainer VRD, 60s, B2B audience with pain points, educational tone
```

### Test Case 4: VRD → Script Flow
```bash
1. VRD agent generates complete VRD
2. ScriptSmith receives VRD
3. ScriptSmith outputs timed, scene-by-scene script
4. Verify script honors VRD timing, audience, messages, tone
```

## Success Metrics

### VRD Quality Checklist
- ✅ All 7 sections present
- ✅ Duration specified
- ✅ Target audience with demographics
- ✅ Pain points identified
- ✅ Key messages defined (core + supporting)
- ✅ CTA clear
- ✅ Timing breakdown provided
- ✅ Tone/style specified

### ScriptSmith Integration Checklist
- ✅ Script matches VRD duration (±5s tolerance)
- ✅ Script addresses pain points from VRD
- ✅ Script includes all key messages
- ✅ Script tone matches VRD specification
- ✅ Script structure follows VRD outline
- ✅ CTA from VRD included verbatim

## Future Enhancements

### Phase 2 (After Sprint 2 testing)
1. **ML-Based Classification**: Replace keyword detection with trained classifier
2. **VRD Validation**: Add schema validation before handoff
3. **User Confirmation**: Add human-in-the-loop checkpoint before script generation
4. **Template Library**: Pre-built VRD templates by industry
5. **Example Integration**: Show reference videos matching VRD specs

### Phase 3 (Production)
1. **User Editing Interface**: Allow users to modify VRD sections
2. **Version Control**: Track VRD changes and script iterations
3. **A/B Testing**: Generate multiple VRD variations
4. **Analytics Integration**: Learn from successful videos
5. **Multimodal Input**: Accept images, videos, PDFs as requirements

## Files Modified

1. **`apps/agents/agents/sub_agents.py`**
   - Lines 16-54: `analyze_requirements()` enhanced
   - Lines 57-124: `define_video_scope()` enhanced
   - Lines 127-233: `create_vrd_agent()` prompt optimized
   - Lines 375-522: `create_script_smith_agent()` prompt optimized

## Next Steps

1. **Test the workflow**:
   ```bash
   cd /home/david/Projects/MVP/PokerCats/apps/agents
   python test_agent.py
   ```

2. **Manual testing**:
   ```bash
   python main.py
   # Then test via API or web interface
   ```

3. **Iterate based on results**:
   - Tune default durations
   - Refine pain point mappings
   - Adjust tone recommendations
   - Improve VRD formatting

## References

- **Example VRD**: `/home/david/Projects/MVP/Example VRD.md`
- **Original System Prompt**: Provided in user request
- **Sprint 2 Documentation**: `/home/david/Projects/MVP/PokerCats/apps/agents/README.md`
- **Scratchpad**: `/home/david/Projects/MVP/scratchpad.md`

---

**Author**: Cascade AI  
**Date**: 2025-11-05  
**Sprint**: Sprint 2 - LangGraph Agent Architecture  
**Status**: ✅ Complete
