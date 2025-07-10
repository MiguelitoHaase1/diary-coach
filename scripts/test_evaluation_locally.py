#!/usr/bin/env python3
"""
Test evaluation system locally.

This script helps test the entire evaluation pipeline locally
before running in CI.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv


def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check API keys
    missing_keys = []
    if not os.getenv("LANGSMITH_API_KEY"):
        missing_keys.append("LANGSMITH_API_KEY")
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        print(f"❌ Missing environment variables: {', '.join(missing_keys)}")
        print("   Please set these in your .env file")
        return False
    
    # Check if baseline exists
    if not Path("baseline_scores.json").exists():
        print("⚠️  No baseline scores found")
        return "no_baseline"
    
    print("✅ All prerequisites met")
    return True


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Exit code: {e.returncode}")
        print(f"   Error output: {e.stderr}")
        return False


async def main():
    """Main test workflow."""
    print("🧪 Testing Evaluation System Locally")
    print("="*50)
    
    # Check prerequisites
    prereq_status = check_prerequisites()
    if prereq_status is False:
        sys.exit(1)
    
    # Step 1: Upload dataset (always do this to ensure it's current)
    print("\n📊 Step 1: Upload Evaluation Dataset")
    if not run_command("python scripts/upload_evaluation_dataset.py", "Upload dataset"):
        print("💡 Try checking your LangSmith API key and project settings")
        sys.exit(1)
    
    # Step 2: Run baseline evaluation (if needed)
    if prereq_status == "no_baseline":
        print("\n🎯 Step 2: Generate Baseline Scores")
        if not run_command("python scripts/run_baseline_eval.py", "Generate baseline"):
            print("💡 Try checking your coaching system and API connections")
            sys.exit(1)
    else:
        print("\n🎯 Step 2: Baseline scores already exist (skipping)")
    
    # Step 3: Run CI evaluation check
    print("\n🔍 Step 3: Run CI Evaluation Check")
    ci_success = run_command("python scripts/ci_eval_check.py", "CI evaluation check")
    
    # Results summary
    print("\n" + "="*50)
    print("📋 LOCAL EVALUATION TEST SUMMARY")
    print("="*50)
    
    if ci_success:
        print("✅ All tests passed! Evaluation system is working correctly.")
        print("💡 You can now safely use 'eval-impact' labels on PRs")
        print("💡 CI will run the same evaluation checks automatically")
    else:
        print("❌ Evaluation detected regressions or issues")
        print("💡 This is what would happen in CI with an 'eval-impact' PR")
        print("💡 Review the detailed output above for specific issues")
    
    # Show next steps
    print(f"\n🎯 Next Steps:")
    print(f"1. Review baseline scores in baseline_scores.json")
    print(f"2. Test with 'eval-impact' label on a PR to see CI in action")
    print(f"3. Update evaluation scenarios as your coach evolves")
    
    print("\n🎉 Local evaluation test complete!")


if __name__ == "__main__":
    asyncio.run(main())