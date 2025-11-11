"""
Startup Dependency Validation
Validates required dependencies and provides actionable error messages
"""

import sys
from typing import Optional
from .observability import (
    get_observability,
    AgentMode,
    DegradationReason,
    logger,
)


class ValidationResult:
    """Result of dependency validation"""
    
    def __init__(self):
        self.passed: bool = True
        self.missing_packages: list[str] = []
        self.import_errors: list[tuple[str, str]] = []  # (module, error)
        self.warnings: list[str] = []
        
    def add_missing_package(self, package: str):
        """Add missing package"""
        self.missing_packages.append(package)
        self.passed = False
        
    def add_import_error(self, module: str, error: str):
        """Add import error"""
        self.import_errors.append((module, error))
        self.passed = False
        
    def add_warning(self, warning: str):
        """Add warning (doesn't fail validation)"""
        self.warnings.append(warning)


def validate_dependencies(strict_mode: bool = False) -> ValidationResult:
    """
    Validate all required and optional dependencies at startup
    
    Args:
        strict_mode: If True, fail on any issue. If False, warn and allow degraded mode.
        
    Returns:
        ValidationResult with details
    """
    result = ValidationResult()
    obs = get_observability()
    
    # Check Pydantic (required for modular tools)
    try:
        import pydantic
        pydantic_version = tuple(int(x) for x in pydantic.VERSION.split('.')[:2])
        
        if pydantic_version < (2, 0):
            result.add_warning(
                f"Pydantic {pydantic.VERSION} found, but >= 2.0.0 required for optimal mode. "
                "Enhanced agents will be unavailable."
            )
            obs.log_mode_change(
                AgentMode.DEGRADED,
                "startup_validation",
                DegradationReason.MISSING_DEPENDENCY,
                {"package": "pydantic>=2.0.0", "found": pydantic.VERSION}
            )
    except ImportError:
        result.add_missing_package("pydantic>=2.0.0")
        obs.log_mode_change(
            AgentMode.DEGRADED,
            "startup_validation",
            DegradationReason.MISSING_DEPENDENCY,
            {"package": "pydantic>=2.0.0"}
        )
    
    # Check modular tools (optional - can fallback)
    try:
        from tools import (
            generate_alt_beats,
            generate_shot_list,
            generate_production_plan,
        )
    except ImportError as e:
        result.add_import_error("tools", str(e))
        obs.log_mode_change(
            AgentMode.DEGRADED,
            "startup_validation",
            DegradationReason.IMPORT_ERROR,
            {"module": "tools", "error": str(e)}
        )
    
    # Check enhanced agents (optional - can fallback)
    try:
        from agents.enhanced_sub_agents import (
            create_enhanced_vrd_agent,
            create_enhanced_script_smith_agent,
            create_enhanced_shot_master_agent,
            create_enhanced_video_solver_agent,
        )
    except ImportError as e:
        result.add_import_error("agents.enhanced_sub_agents", str(e))
        obs.log_mode_change(
            AgentMode.DEGRADED,
            "startup_validation",
            DegradationReason.IMPORT_ERROR,
            {"module": "agents.enhanced_sub_agents", "error": str(e)}
        )
    
    # Check LangChain (required)
    try:
        import langchain
        import langgraph
        import langgraph_supervisor
    except ImportError as e:
        result.add_missing_package("langchain/langgraph packages")
        if strict_mode:
            result.passed = False
    
    # Log validation results
    obs.log_startup_validation(
        validation_passed=result.passed and not result.warnings,
        missing_dependencies=result.missing_packages,
        import_errors=[f"{mod}: {err}" for mod, err in result.import_errors]
    )
    
    return result


def print_validation_report(result: ValidationResult, strict_mode: bool = False):
    """
    Print human-readable validation report
    
    Args:
        result: Validation result
        strict_mode: Whether strict mode is enabled
    """
    
    if result.passed and not result.warnings:
        print("✅ All dependencies validated - optimal mode enabled\n")
        return
    
    # Print issues
    print("\n" + "=" * 80)
    
    if result.missing_packages:
        print("❌ MISSING REQUIRED PACKAGES")
        print("=" * 80)
        print("\n📦 Missing packages:")
        for pkg in result.missing_packages:
            print(f"   - {pkg}")
        print(f"\n✅ Fix: pip install {' '.join(result.missing_packages)}")
        
    if result.import_errors:
        print("\n" + "=" * 80)
        print("⚠️  IMPORT ERRORS DETECTED")
        print("=" * 80)
        print("\n🔧 Import errors:")
        for module, error in result.import_errors:
            print(f"   - {module}: {error}")
        
    if result.warnings:
        print("\n" + "=" * 80)
        print("⚠️  WARNINGS")
        print("=" * 80)
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # Print action items
    print("\n" + "=" * 80)
    print("📖 RECOMMENDED ACTIONS")
    print("=" * 80)
    print("\n1. Install all requirements:")
    print("   pip install -r requirements.txt")
    print("\n2. Verify installation:")
    print("   python -c 'import pydantic; print(pydantic.VERSION)'")
    print("\n3. Check modular tools:")
    print("   python -c 'from tools import generate_alt_beats; print(\"✅\")'")
    
    if not result.passed and strict_mode:
        print("\n❌ STRICT MODE: Application cannot start due to missing dependencies")
        print("=" * 80 + "\n")
        sys.exit(1)
    elif not result.passed or result.warnings:
        print("\n⚠️  DEGRADED MODE: Application will use fallback agents")
        print("   - Reduced functionality")
        print("   - Suboptimal performance")
        print("   - Limited features")
        print("\n📊 Usage is being tracked for optimization")
        print("=" * 80 + "\n")
        
        # Show degradation warning
        get_observability().print_degradation_warning()


def validate_and_report(strict_mode: bool = False) -> bool:
    """
    Validate dependencies and print report
    
    Args:
        strict_mode: If True, exit on validation failure
        
    Returns:
        True if validation passed, False otherwise
    """
    result = validate_dependencies(strict_mode=strict_mode)
    print_validation_report(result, strict_mode=strict_mode)
    
    return result.passed and not result.warnings
