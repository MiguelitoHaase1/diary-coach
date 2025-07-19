#!/bin/bash
# Run integration tests for multi-agent system

echo "Running Multi-Agent Integration Tests..."
echo "======================================="

# Activate virtual environment if it exists
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

# Run the integration tests
echo -e "\n1. Testing Multi-Agent E2E..."
python -m pytest tests/integration/test_multi_agent_e2e.py -v

echo -e "\n2. Testing Agent Collaboration..."
python -m pytest tests/integration/test_agent_collaboration.py -v

echo -e "\n3. Testing LangSmith Integration..."
python -m pytest tests/integration/test_multi_agent_langsmith.py -v

echo -e "\n4. Running all integration tests together..."
python -m pytest tests/integration/test_multi_agent*.py -v --tb=short

echo -e "\nIntegration tests complete!"