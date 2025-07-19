#!/usr/bin/env python3
"""
Run tests excluding evaluation tests.

This script runs the test suite while excluding the evaluation tests
that use personas and simulations, as those are now handled within
the deep think report system.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite excluding evaluation tests."""
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Activate virtual environment if available
    venv_path = os.path.join(project_root, "venv")
    if os.path.exists(venv_path):
        activate_cmd = f"source {venv_path}/bin/activate && "
    else:
        activate_cmd = ""
    
    # Run tests excluding evaluation directory
    cmd = [
        "python", "-m", "pytest", 
        "tests/",
        "--ignore=tests/evaluation/",
        "-v",
        "--tb=short"
    ]
    
    print("🧪 Running tests (excluding evaluation tests)...")
    print("=" * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("- Evaluation tests: SKIPPED (handled in deep think reports)")
    print("- Other tests: See results above")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())