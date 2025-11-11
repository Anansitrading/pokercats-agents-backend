"""
Example Usage of New Modular Multi-Agent System

Demonstrates both YOLO and HITL modes
"""

import json
from workflows import ProductionOrchestrator


def example_yolo_mode():
    """
    Example: Full auto pipeline (no human approval needed)
    Perfect for rapid prototyping and batch processing
    """
    print("=" * 60)
    print("EXAMPLE 1: YOLO MODE (Full Auto)")
    print("=" * 60)
    
    # Initialize orchestrator in YOLO mode
    orchestrator = ProductionOrchestrator(mode="yolo")
    
    # Define VRD
    vrd = {
        'project_name': 'Kijko Product Demo Video',
        'video_type': 'product_demo',
        'estimated_duration': '60s',
        'target_audience': 'B2B decision makers, ages 28-55, SaaS founders',
        'tone': 'empowering',
        'core_message': 'Create professional videos 10x faster with Kijko AI',
        'cta': 'Start Free Trial'
    }
    
    print("\n📝 VRD Input:")
    print(json.dumps(vrd, indent=2))
    
    # Execute full pipeline
    print("\n🚀 Executing full pipeline...")
    result = orchestrator.execute_full_pipeline(vrd)
    
    # Display results
    print("\n✅ Pipeline Complete!")
    print(f"   Mode: {result['mode']}")
    print(f"   Steps: {', '.join(result['steps_completed'])}")
    
    print("\n📊 Summary:")
    print(f"   • Script: {result['summary']['beats']} ALT beats")
    print(f"   • Shots: {result['summary']['shots']} shots planned")
    print(f"   • Cost: ${result['summary']['cost_usd']:.2f}")
    print(f"   • Time: {result['summary']['time_minutes']:.1f} minutes")
    
    # Show script details
    print("\n📖 Script Details:")
    script = result['script']
    print(f"   Title: {script.metadata.title}")
    print(f"   Duration: {script.metadata.duration_seconds}s")
    print(f"   Tone: {script.metadata.tone}")
    print(f"   Structure: {script.structure.total_beats} beats")
    
    print("\n🎬 Sample Beats:")
    for i, beat in enumerate(script.beats[:3], 1):
        print(f"\n   Beat {i} ({beat.narrative_function.eight_part_position}):")
        print(f"   • Timing: {beat.timecode_start} - {beat.timecode_end}")
        print(f"   • Duration: {beat.duration_seconds}s")
        print(f"   • Question: {beat.story_question}")
        print(f"   • Shot: {beat.visual_requirements.shot_type}")
        print(f"   • Complexity: {beat.production_metadata.estimated_complexity}")
    
    # Show shot details
    print("\n🎥 Shot Details:")
    shot_list = result['shot_list']
    print(f"   Total shots: {shot_list.total_shots}")
    print(f"   Unique shot types: {shot_list.asset_summary.total_unique_shot_types}")
    print(f"   VFX shots: {shot_list.asset_summary.vfx_shots}")
    
    print("\n📸 Sample Shots:")
    for i, shot in enumerate(shot_list.shots[:3], 1):
        print(f"\n   Shot {i}:")
        print(f"   • Type: {shot.shot_type}")
        print(f"   • Duration: {shot.duration_seconds}s")
        print(f"   • Camera: {shot.camera_movement}")
        print(f"   • Lighting: {shot.lighting.mood}")
        print(f"   • Complexity: {shot.technical_complexity.complexity_score}/10")
    
    # Show production plan
    print("\n💰 Production Plan:")
    plan = result['production_plan']
    print(f"   Total cost: ${plan.total_estimated_cost_usd:.2f}")
    print(f"   Parallel time: {plan.timeline_estimate.parallel_time_minutes:.1f} min")
    print(f"   Sequential time: {plan.timeline_estimate.sequential_time_minutes:.1f} min")
    
    print("\n🛠️  Primary Tools:")
    for tool, cost in plan.workflow_summary.primary_tools:
        print(f"   • {tool}: ${cost:.2f}")
    
    print("\n📋 Workflow Distribution:")
    for wf_type, count in plan.workflow_summary.workflow_types.items():
        print(f"   • {wf_type}: {count} shots")
    
    # Export JSON
    print("\n💾 Exporting JSON files...")
    
    with open('/tmp/script.json', 'w') as f:
        f.write(script.model_dump_json(indent=2))
    print("   ✅ script.json")
    
    with open('/tmp/shot_list.json', 'w') as f:
        f.write(shot_list.model_dump_json(indent=2))
    print("   ✅ shot_list.json")
    
    with open('/tmp/production_plan.json', 'w') as f:
        f.write(plan.model_dump_json(indent=2))
    print("   ✅ production_plan.json")
    
    return result


def example_hitl_mode():
    """
    Example: Human-in-the-loop mode (requires approval at each stage)
    Perfect for client work and quality control
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: HITL MODE (Human-in-the-Loop)")
    print("=" * 60)
    
    # Initialize orchestrator in HITL mode
    orchestrator = ProductionOrchestrator(mode="hitl")
    
    # Define VRD (minimal - will ask questions)
    vrd = {
        'project_name': 'Brand Story Video',
        'video_type': 'brand_story',
        'estimated_duration': '90s',
        'target_audience': 'Tech-savvy professionals'
    }
    
    print("\n📝 VRD Input (minimal):")
    print(json.dumps(vrd, indent=2))
    
    # Step 1: Set VRD
    print("\n🔍 Step 1: Setting VRD...")
    status = orchestrator.set_vrd(vrd)
    
    if status['status'] == 'needs_clarification':
        print("\n❓ Questions needed:")
        for i, q in enumerate(status['questions'], 1):
            print(f"\n   Q{i}: {q['question']}")
            print(f"       Type: {q['type']}")
            print(f"       Priority: {q['priority']}")
            if q.get('options'):
                print(f"       Options: {', '.join(q['options'])}")
            if q.get('hint'):
                print(f"       Hint: {q['hint']}")
        
        # Simulate user answers
        print("\n💬 User provides answers:")
        clarifications = {
            'core_message': 'Innovation through collaboration',
            'tone': 'inspiring',
            'midpoint_emotion': 'hopeful',
            'act2_emphasis': '60/40 solution',
            'visual_metaphors': 'journey, transformation'
        }
        
        for key, value in clarifications.items():
            print(f"   • {key}: {value}")
        
        orchestrator.provide_clarifications(clarifications)
    
    # Step 2: Generate script
    print("\n📝 Step 2: Generating script...")
    script_result = orchestrator.generate_script()
    
    print(f"   ✅ Script generated: {script_result['beat_count']} beats")
    print(f"   ✅ Duration: {script_result['duration']}s")
    print(f"   ✅ Validation: {script_result['validation']['valid']}")
    
    if script_result.get('approval_required'):
        print("\n   ⏸️  Waiting for user approval...")
        print("   💡 In production, show script preview here")
        print("   ✅ User approves (simulated)")
    
    # Step 3: Generate shots
    print("\n🎬 Step 3: Generating shots...")
    shots_result = orchestrator.generate_shots()
    
    print(f"   ✅ Shots generated: {shots_result['total_shots']}")
    print(f"   ✅ VFX shots: {shots_result['asset_summary'].vfx_shots}")
    print(f"   ✅ Estimated time: {shots_result['asset_summary'].estimated_total_time_minutes:.1f} min")
    
    if shots_result.get('approval_required'):
        print("\n   ⏸️  Waiting for user approval...")
        print("   💡 In production, show storyboard preview here")
        print("   ✅ User approves (simulated)")
    
    # Step 4: Generate plan
    print("\n💰 Step 4: Generating production plan...")
    constraints = {
        'quality_priority': 'high',
        'max_total_cost': 100.0
    }
    plan_result = orchestrator.generate_plan(constraints)
    
    print(f"   ✅ Plan generated")
    print(f"   ✅ Total cost: ${plan_result['total_cost']:.2f}")
    print(f"   ✅ Total time: {plan_result['total_time']:.1f} min")
    print(f"   ✅ Tools used: {plan_result['workflow_summary'].total_unique_tools}")
    
    if plan_result.get('approval_required'):
        print("\n   ⏸️  Waiting for final approval...")
        print("   💡 In production, show cost breakdown and tool selection")
        print("   ✅ User approves (simulated)")
    
    print("\n✅ HITL Pipeline Complete!")
    print(f"   Total steps: {len(orchestrator.steps_completed)}")
    print(f"   Steps: {', '.join(orchestrator.steps_completed)}")
    
    return orchestrator


def example_direct_tools():
    """
    Example: Using tools directly without orchestrator
    Perfect for custom workflows and integration
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Direct Tool Usage")
    print("=" * 60)
    
    from tools import (
        generate_alt_beats,
        validate_alt_beats_timing,
        generate_shot_list,
        generate_production_plan
    )
    
    # Define VRD
    vrd = {
        'video_type': 'social_ad',
        'estimated_duration': '30s',
        'target_audience': 'Social media users, 18-35',
        'tone': 'energetic',
        'core_message': 'Transform your content creation'
    }
    
    print("\n1️⃣  Generate ALT Beats:")
    script = generate_alt_beats(vrd, clarifications={}, mode="yolo")
    print(f"   ✅ Generated {script.total_beat_count} beats")
    
    # Validate timing
    validation = validate_alt_beats_timing(
        script.beats,
        script.metadata.duration_seconds
    )
    print(f"   ✅ Validation: {validation['valid']}")
    print(f"   📊 Duration: {validation['total_duration']}s / {validation['target_duration']}s")
    
    print("\n2️⃣  Generate Shot List:")
    shot_list = generate_shot_list(script.beats, mode="yolo")
    print(f"   ✅ Generated {shot_list.total_shots} shots")
    print(f"   📊 Shot types: {shot_list.asset_summary.total_unique_shot_types}")
    
    print("\n3️⃣  Generate Production Plan:")
    plan = generate_production_plan(
        shot_list,
        constraints={'quality_priority': 'balanced'},
        mode="yolo"
    )
    print(f"   ✅ Plan generated")
    print(f"   💰 Cost: ${plan.total_estimated_cost_usd:.2f}")
    print(f"   ⏱️  Time: {plan.total_estimated_time_minutes:.1f} min")
    
    print("\n📦 Direct tool usage complete!")
    
    return script, shot_list, plan


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Multi-Agent Video Production System - Example Usage      ║")
    print("║  Demonstrating Modular Architecture                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # Run examples
    try:
        # Example 1: YOLO mode (full auto)
        result_yolo = example_yolo_mode()
        
        # Example 2: HITL mode (interactive)
        orchestrator_hitl = example_hitl_mode()
        
        # Example 3: Direct tools
        script, shot_list, plan = example_direct_tools()
        
        print("\n" + "=" * 60)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\n📁 Files exported to /tmp/:")
        print("   • script.json")
        print("   • shot_list.json")
        print("   • production_plan.json")
        print("\n💡 Next steps:")
        print("   1. Review exported JSON files")
        print("   2. Integrate with your API/UI")
        print("   3. Add custom tools or workflows")
        print("   4. Create test suite")
        print("\n🚀 System ready for production use!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
