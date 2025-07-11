"""Test basic LangSmith connection and functionality."""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

print("🔧 Testing LangSmith Connection")
print("=" * 50)

# Check environment
api_key = os.getenv("LANGSMITH_API_KEY")
project = os.getenv("LANGSMITH_PROJECT", "default")

print(f"LANGSMITH_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
print(f"LANGSMITH_PROJECT: {project}")

if not api_key:
    print("\n❌ Please set LANGSMITH_API_KEY environment variable")
    sys.exit(1)

try:
    from langsmith import Client
    print("\n✅ LangSmith imported successfully")
except ImportError:
    print("\n❌ LangSmith not installed. Run: pip install langsmith")
    sys.exit(1)

# Test client creation
try:
    client = Client()
    print("✅ LangSmith client created")
    
    # Test API connectivity by listing datasets
    print("\n📊 Testing API connectivity...")
    datasets = list(client.list_datasets(limit=1))
    print(f"✅ API connection successful (found {len(datasets)} dataset)")
    
except Exception as e:
    print(f"❌ LangSmith client error: {str(e)}")
    sys.exit(1)

# Test creating a simple run
print("\n🧪 Testing run creation...")
try:
    import uuid
    from datetime import datetime
    
    run_id = str(uuid.uuid4())
    
    # Method 1: Using run context manager (recommended)
    from langsmith import traceable
    
    @traceable(name="test_function")
    def test_function(x: int) -> int:
        return x * 2
    
    result = test_function(5)
    print(f"✅ Traceable function executed: 5 * 2 = {result}")
    
    # Method 2: Manual run creation
    run = client.create_run(
        id=run_id,
        name="test_run",
        run_type="chain",
        inputs={"test": "hello"},
        start_time=datetime.now()
    )
    
    # Update run with outputs
    client.update_run(
        run_id,
        outputs={"result": "world"},
        end_time=datetime.now()
    )
    
    print(f"✅ Manual run created: {run_id}")
    print(f"📊 View at: https://smith.langchain.com/o/anthropic/projects/p/{project}")
    
except Exception as e:
    print(f"❌ Run creation error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n✅ LangSmith connection test complete!")