#!/usr/bin/env python3
"""
Run only smoke tests for quick verification.

Smoke tests are designed to quickly verify core functionality
without running the full test suite.
"""

import subprocess
import sys
import os


def run_smoke_tests():
    """Run only smoke tests."""
    # Ensure we're in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Run only smoke tests
    cmd = [
        "python", "-m", "pytest", 
        "-m", "smoke",
        "-v",
        "--tb=short"
    ]
    
    print("🚀 Running smoke tests only...")
    print("=" * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ Smoke tests complete")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_smoke_tests())