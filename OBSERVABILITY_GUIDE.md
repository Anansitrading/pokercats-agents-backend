# 📊 Observability & Graceful Degradation Guide

## Overview

The OpenCut agent system implements **graceful degradation** with comprehensive observability. When enhanced agents are unavailable, the system falls back to legacy agents while tracking usage for optimization.

---

## Architecture

### Operation Modes

1. **Optimal Mode** ✅
   - Enhanced agents with modular tools
   - Pydantic v2 data validation
   - Full feature set
   - Best performance

2. **Degraded Mode** ⚠️
   - Legacy fallback agents
   - Basic functionality
   - Reduced features
   - Suboptimal performance

3. **Failed Mode** ❌
   - Critical dependencies missing
   - System cannot start (strict mode only)

---

## Observability Components

### 1. Structured Logging (`agents/observability.py`)

**JSON-formatted logs** for production monitoring:

```python
{
  "timestamp": "2025-01-06T00:24:00Z",
  "level": "WARNING",
  "logger": "opencut.agents",
  "message": "Agent mode changed: optimal → degraded",
  "component": "supervisor",
  "mode": "degraded",
  "degradation_reason": "import_error"
}
```

**Key Events Tracked:**
- `agent_mode_change` - Mode transitions
- `fallback_triggered` - Fallback agent usage
- `startup_validation` - Dependency check results

### 2. Startup Validation (`agents/startup_validation.py`)

**Validates dependencies on startup:**

```bash
🚀 Starting OpenCut Agent System...

⚠️ IMPORT ERRORS DETECTED
================================================================================
🔧 Import errors:
   - tools: No module named 'pydantic'

📖 RECOMMENDED ACTIONS
================================================================================
1. Install all requirements:
   pip install -r requirements.txt
```

**Validation Checks:**
- ✅ Pydantic >= 2.0.0
- ✅ Modular tools importable
- ✅ Enhanced agents available
- ✅ LangChain/LangGraph present

### 3. Metrics Tracking

**Real-time degradation metrics:**

```python
from agents.observability import get_observability

metrics = get_observability().get_degradation_metrics()
# {
#   "current_mode": "degraded",
#   "fallback_count": 3,
#   "degradation_reasons": ["import_error"],
#   "time_in_degraded_mode_seconds": 1245.6
# }
```

---

## Integration Guide

### Log Mode Changes

```python
from agents.observability import get_observability, AgentMode, DegradationReason

obs = get_observability()

# Log entering degraded mode
obs.log_mode_change(
    AgentMode.DEGRADED,
    component="my_component",
    reason=DegradationReason.MISSING_DEPENDENCY,
    details={"package": "pydantic>=2.0.0"}
)
```

### Track Fallback Usage

```python
# When using fallback instead of primary implementation
obs.log_fallback_triggered(
    agent_id="script_smith",
    fallback_strategy="legacy_alt_beats",
    reason="pydantic_v2_unavailable",
    input_context={"video_type": "explainer"}
)
```

### Startup Validation

```python
from agents.startup_validation import validate_and_report

# Validate with warnings (recommended)
optimal = validate_and_report(strict_mode=False)

# Validate with strict failure
optimal = validate_and_report(strict_mode=True)  # Exits if issues found
```

---

## Monitoring Recommendations

### 1. Log Aggregation

**Recommended Stack:**
- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Datadog**: Cloud-native monitoring
- **New Relic**: APM with log management

**Setup Example (Datadog):**

```python
import logging
from datadog import statsd

# Emit metrics on mode change
if mode == AgentMode.DEGRADED:
    statsd.increment('opencut.agents.degraded_mode', 
                     tags=['component:supervisor'])
```

### 2. Alerting Rules

**Recommended Alerts:**

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Fallback Rate | >10 fallbacks/hour | WARNING |
| Sustained Degradation | Degraded mode >1 hour | WARNING |
| Critical Failure | Failed mode | CRITICAL |
| Dependency Missing | Startup validation fails | WARNING |

**Example (Prometheus/Alertmanager):**

```yaml
- alert: HighFallbackRate
  expr: rate(opencut_fallback_count[1h]) > 10
  annotations:
    summary: "High fallback usage detected"
    description: "Fallback agents used {{ $value }} times in last hour"
```

### 3. Dashboard Widgets

**Key Metrics to Track:**

1. **Mode Distribution** (Pie Chart)
   - % time in optimal mode
   - % time in degraded mode
   
2. **Fallback Count** (Time Series)
   - Fallbacks per hour
   - Trend over time

3. **Degradation Reasons** (Bar Chart)
   - Import errors
   - Missing dependencies
   - Configuration issues

4. **Response Times** (Histogram)
   - Optimal mode latency
   - Degraded mode latency
   - Comparison

---

## Best Practices

### 1. Don't Hide Degradation

❌ **Bad:**
```python
try:
    result = enhanced_function()
except:
    result = fallback_function()  # Silent fallback
```

✅ **Good:**
```python
try:
    result = enhanced_function()
except Exception as e:
    logger.warning(f"Falling back: {e}")
    obs.log_fallback_triggered(...)
    result = fallback_function()
```

### 2. Fail Fast on Critical Paths

```python
# Critical dependency - no fallback
if not has_critical_dependency():
    raise RuntimeError("Critical dependency missing - cannot start")

# Optional feature - graceful degradation OK
if not has_optional_feature():
    logger.warning("Optional feature unavailable - using fallback")
```

### 3. User Communication

**Clear, actionable messages:**

```
⚠️  DEGRADED MODE ACTIVE
================================================================================
🔧 The agent system is running with fallback capabilities.
   Some features may not be available or may perform suboptimally.

📋 Reasons:
   - missing_dependency: pydantic>=2.0.0

✅ To enable optimal mode:
   1. Ensure all dependencies installed: pip install -r requirements.txt
   2. Verify Pydantic >= 2.0.0
   3. Check that modular tools are importable
```

### 4. Testing Degraded Paths

**Always test fallback scenarios:**

```python
# test_degraded_mode.py
def test_fallback_agents_work():
    """Verify system works when enhanced agents unavailable"""
    # Simulate missing pydantic
    with mock.patch.dict('sys.modules', {'pydantic': None}):
        result = create_supervisor_workflow()
        assert result is not None  # Should use fallback
```

---

## Production Checklist

- [ ] Structured logging enabled
- [ ] Log aggregation configured
- [ ] Alerting rules deployed
- [ ] Monitoring dashboard created
- [ ] Fallback paths tested
- [ ] User warnings implemented
- [ ] Metrics tracked in production
- [ ] Runbook for degraded mode created

---

## Troubleshooting

### High Fallback Rate

**Investigate:**
1. Check dependency versions: `pip list | grep pydantic`
2. Review import errors in logs
3. Verify virtual environment activated
4. Check for conflicting packages

**Fix:**
```bash
pip install --upgrade -r requirements.txt
python -c "from agents.enhanced_sub_agents import *"  # Verify imports
```

### Sustained Degraded Mode

**Root Causes:**
- Dependency installation failed
- Version conflicts
- Import path issues
- Configuration errors

**Resolution:**
1. Run validation: `python -m agents.startup_validation`
2. Review structured logs for errors
3. Reinstall dependencies: `pip install --force-reinstall -r requirements.txt`
4. Check Python version compatibility

---

## Future Enhancements

### Phase 2: Advanced Observability

- [ ] Distributed tracing (OpenTelemetry)
- [ ] Custom metrics export (Prometheus format)
- [ ] Real-time alerts to Slack/PagerDuty
- [ ] Automatic remediation for common issues
- [ ] Chaos testing for degradation scenarios

### Phase 3: Self-Healing

- [ ] Auto-retry with dependency installation
- [ ] Dynamic feature flags
- [ ] A/B testing optimal vs degraded
- [ ] ML-based anomaly detection

---

## References

- [AWS Well-Architected: Graceful Degradation](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_graceful_degradation.html)
- [New Relic: Design for Graceful Degradation](https://newrelic.com/blog/best-practices/design-software-for-graceful-degradation)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/specs/otel/logs/)
- [Structured Logging Best Practices](https://www.dataset.com/blog/the-10-commandments-of-logging/)

---

**Last Updated:** 2025-01-06  
**Sprint:** 3 Preparation  
**Status:** ✅ Implementation Complete
