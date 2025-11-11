"""
Production Orchestrator
Coordinates multi-agent video production pipeline
Supports both HITL (human-in-the-loop) and YOLO (full auto) modes
"""

from typing import Literal
from models.alt_beat import Script
from models.shot import ShotList
from models.production_plan import ProductionPlan
from tools import (
    generate_alt_beats,
    validate_alt_beats_timing,
    ask_clarifying_questions,
    apply_clarifications_to_vrd,
    generate_shot_list,
    generate_production_plan
)


class ProductionOrchestrator:
    """
    Orchestrates the full production pipeline
    VRD → Script (ALT Beats) → Shot List → Production Plan
    """
    
    def __init__(self, mode: Literal["hitl", "yolo"] = "hitl"):
        """
        Initialize orchestrator
        
        Args:
            mode: 'hitl' for human-in-the-loop, 'yolo' for full auto
        """
        self.mode = mode
        self.require_approval = mode == "hitl"
        
        # Pipeline state
        self.vrd = None
        self.clarifications = {}
        self.script = None
        self.shot_list = None
        self.production_plan = None
        
        # Pipeline steps
        self.current_step = "vrd_input"
        self.steps_completed = []
    
    def set_vrd(self, vrd: dict) -> dict:
        """
        Set VRD and prepare for scriptwriting
        
        Args:
            vrd: Video Requirements Document
            
        Returns:
            Status and next actions
        """
        self.vrd = vrd
        self.current_step = "vrd_received"
        self.steps_completed.append("vrd_input")
        
        # Check if we need clarifications
        if self.mode == "hitl":
            questions = ask_clarifying_questions(vrd, self.mode)
            if questions:
                self.current_step = "awaiting_clarifications"
                return {
                    'status': 'needs_clarification',
                    'questions': questions,
                    'next_action': 'provide_clarifications'
                }
        
        return {
            'status': 'ready_for_script',
            'next_action': 'generate_script'
        }
    
    def provide_clarifications(self, clarifications: dict) -> dict:
        """
        Receive user clarifications
        
        Args:
            clarifications: User responses to questions
            
        Returns:
            Status
        """
        self.clarifications = clarifications
        self.vrd = apply_clarifications_to_vrd(self.vrd, clarifications)
        self.current_step = "clarifications_received"
        self.steps_completed.append("clarifications")
        
        return {
            'status': 'ready_for_script',
            'next_action': 'generate_script'
        }
    
    def generate_script(self) -> dict:
        """
        Generate script with ALT beats
        
        Returns:
            Script object and status
        """
        if not self.vrd:
            return {'status': 'error', 'message': 'VRD not set'}
        
        # Generate ALT beats
        self.script = generate_alt_beats(self.vrd, self.clarifications, self.mode)
        
        # Validate timing
        validation = validate_alt_beats_timing(
            self.script.beats,
            self.script.metadata.duration_seconds
        )
        
        self.current_step = "script_generated"
        self.steps_completed.append("script_generation")
        
        result = {
            'status': 'script_generated',
            'script': self.script,
            'validation': validation,
            'beat_count': self.script.total_beat_count,
            'duration': self.script.metadata.duration_seconds
        }
        
        if self.mode == "hitl":
            result['next_action'] = 'review_script_then_generate_shots'
            result['approval_required'] = True
        else:
            result['next_action'] = 'generate_shots'
            result['approval_required'] = False
        
        return result
    
    def generate_shots(self) -> dict:
        """
        Generate shot list from script
        
        Returns:
            Shot list and status
        """
        if not self.script:
            return {'status': 'error', 'message': 'Script not generated'}
        
        # Generate shots
        self.shot_list = generate_shot_list(self.script.beats, self.mode)
        
        self.current_step = "shots_generated"
        self.steps_completed.append("shot_generation")
        
        result = {
            'status': 'shots_generated',
            'shot_list': self.shot_list,
            'total_shots': self.shot_list.total_shots,
            'asset_summary': self.shot_list.asset_summary
        }
        
        if self.mode == "hitl":
            result['next_action'] = 'review_shots_then_generate_plan'
            result['approval_required'] = True
        else:
            result['next_action'] = 'generate_plan'
            result['approval_required'] = False
        
        return result
    
    def generate_plan(self, constraints: dict = None) -> dict:
        """
        Generate production plan with tool selection
        
        Args:
            constraints: Optional constraints (quality_priority, max_cost, etc.)
            
        Returns:
            Production plan and status
        """
        if not self.shot_list:
            return {'status': 'error', 'message': 'Shot list not generated'}
        
        # Generate production plan
        self.production_plan = generate_production_plan(
            self.shot_list,
            constraints,
            self.mode
        )
        
        self.current_step = "plan_generated"
        self.steps_completed.append("plan_generation")
        
        result = {
            'status': 'plan_generated',
            'production_plan': self.production_plan,
            'total_cost': self.production_plan.total_estimated_cost_usd,
            'total_time': self.production_plan.total_estimated_time_minutes,
            'workflow_summary': self.production_plan.workflow_summary
        }
        
        if self.mode == "hitl":
            result['next_action'] = 'review_plan_then_execute'
            result['approval_required'] = True
        else:
            result['next_action'] = 'execute_production'
            result['approval_required'] = False
        
        return result
    
    def execute_full_pipeline(self, vrd: dict, constraints: dict = None) -> dict:
        """
        Execute complete pipeline in one go (YOLO mode recommended)
        
        Args:
            vrd: Video Requirements Document
            constraints: Optional production constraints
            
        Returns:
            Complete pipeline results
        """
        # Step 1: Set VRD
        vrd_result = self.set_vrd(vrd)
        
        if vrd_result['status'] == 'needs_clarification' and self.mode == "hitl":
            return vrd_result  # Need user input
        
        # Step 2: Generate script
        script_result = self.generate_script()
        
        if script_result.get('approval_required') and self.mode == "hitl":
            return script_result  # Need approval
        
        # Step 3: Generate shots
        shots_result = self.generate_shots()
        
        if shots_result.get('approval_required') and self.mode == "hitl":
            return shots_result  # Need approval
        
        # Step 4: Generate plan
        plan_result = self.generate_plan(constraints)
        
        return {
            'status': 'pipeline_complete',
            'mode': self.mode,
            'steps_completed': self.steps_completed,
            'script': self.script,
            'shot_list': self.shot_list,
            'production_plan': self.production_plan,
            'summary': {
                'beats': self.script.total_beat_count,
                'shots': self.shot_list.total_shots,
                'cost_usd': self.production_plan.total_estimated_cost_usd,
                'time_minutes': self.production_plan.total_estimated_time_minutes
            }
        }
    
    def get_status(self) -> dict:
        """Get current pipeline status"""
        return {
            'mode': self.mode,
            'current_step': self.current_step,
            'steps_completed': self.steps_completed,
            'has_vrd': self.vrd is not None,
            'has_script': self.script is not None,
            'has_shots': self.shot_list is not None,
            'has_plan': self.production_plan is not None
        }
