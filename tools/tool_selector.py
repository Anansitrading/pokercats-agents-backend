"""
Tool Selection Tools
Selects optimal AI video generation tools based on SOTA research
"""

import csv
from pathlib import Path
from datetime import datetime
from models.shot import Shot, ShotList
from models.production_plan import (
    ProductionPlan, ShotPlan, Workflow, WorkflowStep,
    WorkflowSummary, CostBreakdown, TimelineEstimate
)


# SOTA tool recommendations (from Perplexity research 2025)
SOTA_TOOL_RECOMMENDATIONS = {
    'wide': {
        'high_quality': {
            'tool': 'Google Veo 3',
            'score': 9.7,
            'cost_per_second': 0.08,
            'reason': '4K, physics realism, native audio'
        },
        'balanced': {
            'tool': 'Runway Gen-3 Alpha',
            'score': 9.3,
            'cost_per_second': 0.05,
            'reason': 'Industry standard, reliable'
        },
        'budget': {
            'tool': 'Luma Dream Machine 1.6',
            'score': 9.1,
            'cost_per_second': 0.08,
            'reason': 'Fast generation, cinematic'
        }
    },
    'extreme_wide': {
        'high_quality': {
            'tool': 'OpenAI Sora',
            'score': 9.6,
            'cost_per_second': 0.10,
            'reason': 'Long-form, scene continuity'
        },
        'balanced': {
            'tool': 'Google Veo 3',
            'score': 9.7,
            'cost_per_second': 0.08,
            'reason': 'Epic scale, physics'
        },
        'budget': {
            'tool': 'Kling AI 1.5/2.1',
            'score': 9.2,
            'cost_per_second': 0.06,
            'reason': 'Good quality, affordable'
        }
    },
    'closeup': {
        'high_quality': {
            'tool': 'Kling AI 1.5/2.1',
            'score': 9.2,
            'cost_per_second': 0.06,
            'reason': 'Best lip-sync, facial realism'
        },
        'balanced': {
            'tool': 'Runway Gen-3 Alpha',
            'score': 9.3,
            'cost_per_second': 0.05,
            'reason': 'Character consistency'
        },
        'budget': {
            'tool': 'Haiper AI',
            'score': 8.6,
            'cost_per_second': 0.05,
            'reason': 'Fast, cost-effective'
        }
    },
    'medium_closeup': {
        'high_quality': {
            'tool': 'Kling AI 1.5/2.1',
            'score': 9.2,
            'cost_per_second': 0.06,
            'reason': 'Photorealism, detail'
        },
        'balanced': {
            'tool': 'Runway Gen-3 Alpha',
            'score': 9.3,
            'cost_per_second': 0.05,
            'reason': 'Reliable quality'
        },
        'budget': {
            'tool': 'Haiper AI',
            'score': 8.6,
            'cost_per_second': 0.05,
            'reason': 'Quick generation'
        }
    },
    'medium': {
        'high_quality': {
            'tool': 'Runway Gen-3 Alpha',
            'score': 9.3,
            'cost_per_second': 0.05,
            'reason': 'Best all-around'
        },
        'balanced': {
            'tool': 'Luma Dream Machine 1.6',
            'score': 9.1,
            'cost_per_second': 0.08,
            'reason': 'Fast, reliable'
        },
        'budget': {
            'tool': 'Haiper AI',
            'score': 8.6,
            'cost_per_second': 0.05,
            'reason': 'Cost-effective'
        }
    },
    'medium_wide': {
        'high_quality': {
            'tool': 'Runway Gen-3 Alpha',
            'score': 9.3,
            'cost_per_second': 0.05,
            'reason': 'Scene composition'
        },
        'balanced': {
            'tool': 'Luma Dream Machine 1.6',
            'score': 9.1,
            'cost_per_second': 0.08,
            'reason': 'Good balance'
        },
        'budget': {
            'tool': 'Haiper AI',
            'score': 8.6,
            'cost_per_second': 0.05,
            'reason': 'Affordable'
        }
    }
}


# VFX tool (always Runway for effects)
VFX_TOOL = {
    'tool': 'Runway Gen-3 Alpha',
    'cost_per_second': 0.05,
    'fixed_cost': 0.15,
    'reason': 'Best VFX and stylization'
}


def load_tool_stack_db(csv_path: str = "/home/david/Projects/MVP/Video Solver - Tool Stack.csv") -> list[dict]:
    """
    Load Tool Stack database from CSV
    
    Args:
        csv_path: Path to tool stack CSV
        
    Returns:
        List of tool dictionaries
    """
    tools = []
    path = Path(csv_path)
    
    if not path.exists():
        return []
    
    try:
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tools.append(row)
    except Exception as e:
        print(f"Error loading tool stack: {e}")
    
    return tools


def select_optimal_tool_for_shot(
    shot: Shot,
    constraints: dict = None
) -> Workflow:
    """
    Select optimal AI tool for generating a specific shot
    
    Based on Perplexity research:
    - Wide shots → Google Veo 3 or Sora 2
    - Closeups → Kling AI 2.1
    - VFX → Runway Gen-4
    - Budget → Haiper AI or Luma
    
    Args:
        shot: Shot specification
        constraints: Optional constraints (quality_priority, max_cost_per_shot)
        
    Returns:
        Recommended Workflow
    """
    constraints = constraints or {}
    quality_priority = constraints.get('quality_priority', 'balanced')
    
    shot_type = shot.shot_type
    duration = shot.duration_seconds
    requires_vfx = shot.technical_complexity.requires_vfx
    
    # Get recommendation from SOTA map
    shot_category = shot_type if shot_type in SOTA_TOOL_RECOMMENDATIONS else 'medium'
    tool_rec = SOTA_TOOL_RECOMMENDATIONS[shot_category].get(quality_priority, SOTA_TOOL_RECOMMENDATIONS[shot_category]['balanced'])
    
    # Calculate cost
    estimated_cost = duration * tool_rec['cost_per_second']
    estimated_time = 45 + (duration * 2)  # Base time + duration factor
    
    # Determine workflow type
    workflow_type = 'text_to_video' if duration > 5 else 'image_to_video'
    
    # Build workflow steps
    steps = [
        WorkflowStep(
            step=1,
            tool=tool_rec['tool'],
            purpose=f'Generate {shot_type} shot',
            workflow_type=workflow_type,
            duration_seconds=duration,
            estimated_time_seconds=estimated_time,
            cost_usd=round(estimated_cost, 2)
        )
    ]
    
    total_cost = estimated_cost
    total_time = estimated_time
    
    # Add VFX step if needed
    if requires_vfx:
        vfx_step = WorkflowStep(
            step=2,
            tool=VFX_TOOL['tool'],
            purpose='Add VFX and effects',
            workflow_type='video_to_video',
            duration_seconds=0,
            estimated_time_seconds=30,
            cost_usd=VFX_TOOL['fixed_cost']
        )
        steps.append(vfx_step)
        total_cost += VFX_TOOL['fixed_cost']
        total_time += 30
    
    workflow = Workflow(
        workflow_id=f'workflow_{shot.shot_id}',
        workflow_name=f'{shot_type.replace("_", " ").title()} - {quality_priority.title()} Quality',
        steps=steps,
        total_cost=round(total_cost, 2),
        total_time_seconds=total_time,
        quality_score=tool_rec['score']
    )
    
    return workflow


def generate_production_plan(
    shot_list: ShotList,
    constraints: dict = None,
    mode: str = "hitl"
) -> ProductionPlan:
    """
    Generate complete production plan with tool selection for all shots
    
    Args:
        shot_list: Shot list from ShotMaster
        constraints: Optional budget/time/quality constraints
        mode: 'hitl' or 'yolo'
        
    Returns:
        Complete ProductionPlan object
    """
    constraints = constraints or {'quality_priority': 'balanced'}
    
    shot_plans = []
    total_cost = 0.0
    total_time = 0
    tools_used = {}
    
    for shot in shot_list.shots:
        # Generate recommended workflow
        recommended = select_optimal_tool_for_shot(shot, constraints)
        
        # Generate alternative (budget option)
        budget_constraints = {**constraints, 'quality_priority': 'budget'}
        alternative = select_optimal_tool_for_shot(shot, budget_constraints)
        
        # Build shot plan
        shot_plan = ShotPlan(
            shot_id=shot.shot_id,
            shot_description=f'{shot.shot_type} - {shot.duration_seconds}s',
            recommended_workflow=recommended,
            alternative_workflows=[alternative] if alternative.total_cost != recommended.total_cost else [],
            production_notes=[
                f'Shot complexity: {shot.technical_complexity.complexity_score}/10',
                f'Estimated generation: {recommended.total_time_seconds}s',
                f'Tool: {recommended.steps[0].tool}'
            ]
        )
        
        shot_plans.append(shot_plan)
        total_cost += recommended.total_cost
        total_time += recommended.total_time_seconds
        
        # Track tool usage
        for step in recommended.steps:
            tool_name = step.tool
            tools_used[tool_name] = tools_used.get(tool_name, 0.0) + step.cost_usd
    
    # Build workflow summary
    primary_tools = sorted(tools_used.items(), key=lambda x: x[1], reverse=True)[:3]
    
    workflow_types = {
        'text_to_video': sum(1 for p in shot_plans if p.recommended_workflow.steps[0].workflow_type == 'text_to_video'),
        'image_to_video': sum(1 for p in shot_plans if p.recommended_workflow.steps[0].workflow_type == 'image_to_video'),
        'video_to_video': sum(1 for p in shot_plans for s in p.recommended_workflow.steps if s.workflow_type == 'video_to_video')
    }
    
    workflow_summary = WorkflowSummary(
        total_unique_tools=len(tools_used),
        primary_tools=primary_tools,
        workflow_types=workflow_types
    )
    
    # Build cost breakdown
    cost_breakdown = CostBreakdown(
        by_tool=tools_used
    )
    
    # Build timeline estimate
    max_shot_time = max(s.recommended_workflow.total_time_seconds for s in shot_plans) if shot_plans else 0
    
    timeline_estimate = TimelineEstimate(
        parallel_generation=True,
        sequential_time_minutes=round(total_time / 60, 1),
        parallel_time_minutes=round(max_shot_time / 60, 1),
        post_processing_minutes=30
    )
    
    # Assemble production plan
    plan = ProductionPlan(
        production_plan_id=f'plan_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        shot_list_ref=shot_list.shot_list_id,
        mode=mode,
        total_estimated_cost_usd=round(total_cost, 2),
        total_estimated_time_minutes=round(total_time / 60, 1),
        shot_plans=shot_plans,
        workflow_summary=workflow_summary,
        cost_breakdown=cost_breakdown,
        timeline_estimate=timeline_estimate
    )
    
    return plan
