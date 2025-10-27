"""Smoke tests for basic functionality and imports."""

import pytest
import sys
import os


def test_imports():
    """Test that all core modules can be imported."""
    # Test core imports
    from src.core.messages import AgentMessage, DebateResult, AgentRole
    from src.core.orchestrator import DebateOrchestrator
    from src.utils.llm_client import LLMClient, MockLLM

    # Verify classes are accessible
    assert AgentMessage is not None
    assert DebateResult is not None
    assert AgentRole is not None
    assert DebateOrchestrator is not None
    assert LLMClient is not None
    assert MockLLM is not None


def test_package_structure():
    """Test that package structure exists."""
    import src
    import src.core
    import src.utils
    import src.app

    assert hasattr(src, "__version__")


def test_mock_llm_without_api_key():
    """Test that MockLLM works without any API key."""
    # Ensure no API key is set
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    from src.utils.llm_client import LLMClient

    # Should default to MockLLM
    client = LLMClient()
    response = client.generate("test prompt")

    assert isinstance(response, str)
    assert len(response) > 0


def test_orchestrator_without_api_key():
    """Test that orchestrator works without API key."""
    # Ensure no API key is set
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    from src.core.orchestrator import DebateOrchestrator

    orchestrator = DebateOrchestrator(max_rounds=1)
    orchestrator.start_debate("Test case")
    orchestrator.step()
    result = orchestrator.evaluate()

    assert result.topic == "Test case"
    assert len(result.messages) > 0


def test_app_shim_exists():
    """Test that app.py shim exists at root."""
    root_app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    assert os.path.exists(root_app_path), "app.py should exist at repository root"


def test_streamlit_import_without_running():
    """Test that streamlit components can be imported without API key."""
    # This test just verifies imports work
    # We don't actually run streamlit
    try:
        import streamlit as st

        # Just verify it imports
        assert st is not None
    except ImportError:
        pytest.skip("Streamlit not installed")


def test_enum_values():
    """Test that AgentRole enum has correct values."""
    from src.core.messages import AgentRole

    assert AgentRole.PROSECUTION.value == "prosecution"
    assert AgentRole.DEFENSE.value == "defense"
    assert AgentRole.JUDGE.value == "judge"


def test_basic_message_creation():
    """Test creating basic messages."""
    from src.core.messages import AgentMessage, AgentRole

    msg = AgentMessage(
        role=AgentRole.PROSECUTION, content="Test content", round_number=1
    )

    assert msg.role == AgentRole.PROSECUTION
    assert msg.content == "Test content"
    assert msg.round_number == 1


def test_basic_result_creation():
    """Test creating basic debate result."""
    from src.core.messages import DebateResult, AgentRole

    result = DebateResult(
        topic="Test topic",
        winner=AgentRole.PROSECUTION,
        judge_reasoning="Test reasoning",
    )

    assert result.topic == "Test topic"
    assert result.winner == AgentRole.PROSECUTION
    assert result.judge_reasoning == "Test reasoning"


def test_no_external_dependencies_for_core():
    """Test that core modules don't require external API access."""
    # This ensures the core logic works offline
    os.environ["MOCK_LLM"] = "true"

    from src.core.orchestrator import DebateOrchestrator

    orchestrator = DebateOrchestrator()
    orchestrator.start_debate("Offline test")
    messages = orchestrator.step()

    # Should work without network
    assert len(messages) == 2

    # Cleanup
    del os.environ["MOCK_LLM"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
