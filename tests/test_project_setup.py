"""Test project setup and imports work correctly."""


def test_project_imports():
    """Verify core modules can be imported"""
    import src.agents
    import src.events
    import src.evaluation
    assert True