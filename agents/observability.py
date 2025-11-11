"""
Observability and Graceful Degradation Logging
Structured logging for multi-agent system with fallback tracking
"""

import logging
import json
import time
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class DegradationReason(Enum):
    """Reasons for entering degraded mode"""
    MISSING_DEPENDENCY = "missing_dependency"
    IMPORT_ERROR = "import_error"
    CONFIGURATION_ERROR = "configuration_error"
    FEATURE_UNAVAILABLE = "feature_unavailable"


class AgentMode(Enum):
    """Agent operation modes"""
    OPTIMAL = "optimal"           # Enhanced agents with modular tools
    DEGRADED = "degraded"         # Legacy fallback agents
    FAILED = "failed"             # System cannot start


# Configure structured logging
def setup_structured_logging():
    """Configure JSON structured logging for production observability"""
    
    class StructuredFormatter(logging.Formatter):
        """JSON formatter for structured logs"""
        
        def format(self, record: logging.LogRecord) -> str:
            log_obj = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra fields if present
            if hasattr(record, 'agent_id'):
                log_obj['agent_id'] = record.agent_id
            if hasattr(record, 'mode'):
                log_obj['mode'] = record.mode
            if hasattr(record, 'degradation_reason'):
                log_obj['degradation_reason'] = record.degradation_reason
            if hasattr(record, 'component'):
                log_obj['component'] = record.component
            if hasattr(record, 'correlation_id'):
                log_obj['correlation_id'] = record.correlation_id
                
            return json.dumps(log_obj)
    
    # Set up root logger
    root_logger = logging.getLogger()
    
    # Add structured handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)


# Create logger for agent system
logger = logging.getLogger("opencut.agents")


class AgentSystemObservability:
    """
    Observability tracker for multi-agent system
    Tracks mode, fallback events, and performance metrics
    """
    
    def __init__(self):
        self.current_mode: AgentMode = AgentMode.OPTIMAL
        self.fallback_count: int = 0
        self.degradation_start_time: Optional[float] = None
        self.degradation_reasons: list[str] = []
        
    def log_mode_change(
        self,
        new_mode: AgentMode,
        component: str,
        reason: Optional[DegradationReason] = None,
        details: Optional[dict[str, Any]] = None
    ):
        """
        Log agent mode change with full context
        
        Args:
            new_mode: New operation mode
            component: Component triggering mode change
            reason: Reason for degradation (if applicable)
            details: Additional context
        """
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        log_level = logging.INFO
        if new_mode == AgentMode.DEGRADED:
            log_level = logging.WARNING
            self.degradation_start_time = time.time()
            if reason:
                self.degradation_reasons.append(reason.value)
        elif new_mode == AgentMode.FAILED:
            log_level = logging.ERROR
            
        event = {
            "event": "agent_mode_change",
            "component": component,
            "old_mode": old_mode.value,
            "new_mode": new_mode.value,
            "degradation_reason": reason.value if reason else None,
            "details": details or {},
        }
        
        logger.log(
            log_level,
            f"Agent mode changed: {old_mode.value} → {new_mode.value}",
            extra={
                "component": component,
                "mode": new_mode.value,
                "degradation_reason": reason.value if reason else None,
            }
        )
        
        # Emit structured event
        self._emit_event(event)
        
    def log_fallback_triggered(
        self,
        agent_id: str,
        fallback_strategy: str,
        reason: str,
        input_context: Optional[dict] = None
    ):
        """
        Log when fallback agent is used instead of enhanced agent
        
        Args:
            agent_id: Agent identifier
            fallback_strategy: Name of fallback strategy
            reason: Why fallback was triggered
            input_context: Sanitized input context
        """
        self.fallback_count += 1
        
        event = {
            "event": "fallback_triggered",
            "agent_id": agent_id,
            "strategy": fallback_strategy,
            "reason": reason,
            "fallback_count": self.fallback_count,
            "input_context": input_context or {},
        }
        
        logger.warning(
            f"Fallback triggered for {agent_id}: {reason}",
            extra={
                "agent_id": agent_id,
                "mode": "degraded",
                "component": "agent_executor",
            }
        )
        
        self._emit_event(event)
        
    def log_startup_validation(
        self,
        validation_passed: bool,
        missing_dependencies: list[str],
        import_errors: list[str]
    ):
        """
        Log startup dependency validation results
        
        Args:
            validation_passed: Whether all dependencies available
            missing_dependencies: List of missing packages
            import_errors: List of import error messages
        """
        event = {
            "event": "startup_validation",
            "validation_passed": validation_passed,
            "missing_dependencies": missing_dependencies,
            "import_errors": import_errors,
        }
        
        if validation_passed:
            logger.info("✅ Startup validation passed - optimal mode available")
        else:
            logger.warning(
                "⚠️  Startup validation detected issues - degraded mode may be used",
                extra={
                    "component": "startup",
                    "mode": "degraded",
                }
            )
            
        self._emit_event(event)
        
    def get_degradation_metrics(self) -> dict[str, Any]:
        """
        Get current degradation metrics for monitoring
        
        Returns:
            Dictionary with current metrics
        """
        metrics = {
            "current_mode": self.current_mode.value,
            "fallback_count": self.fallback_count,
            "degradation_reasons": self.degradation_reasons,
        }
        
        if self.degradation_start_time:
            metrics["time_in_degraded_mode_seconds"] = time.time() - self.degradation_start_time
            
        return metrics
    
    def _emit_event(self, event: dict):
        """
        Emit structured event (can be extended to send to metrics systems)
        
        Args:
            event: Event dictionary
        """
        # For now, just log as JSON
        # In production, integrate with Datadog, Prometheus, etc.
        logger.debug(f"Event: {json.dumps(event)}")
        
    def print_degradation_warning(self):
        """
        Print user-facing warning about degraded mode
        """
        if self.current_mode == AgentMode.DEGRADED:
            print("\n" + "=" * 80)
            print("⚠️  DEGRADED MODE ACTIVE")
            print("=" * 80)
            print("\n🔧 The agent system is running with fallback capabilities.")
            print("   Some features may not be available or may perform suboptimally.\n")
            
            if self.degradation_reasons:
                print("📋 Reasons:")
                for reason in set(self.degradation_reasons):
                    print(f"   - {reason}")
                    
            print("\n✅ To enable optimal mode:")
            print("   1. Ensure all dependencies installed: pip install -r requirements.txt")
            print("   2. Verify Pydantic >= 2.0.0")
            print("   3. Check that modular tools are importable")
            print("   4. Review logs for specific import errors\n")
            print("📊 This usage is being tracked for system optimization.")
            print("=" * 80 + "\n")


# Global observability instance
observability = AgentSystemObservability()


def get_observability() -> AgentSystemObservability:
    """Get global observability instance"""
    return observability


# Initialize structured logging on module import
setup_structured_logging()
