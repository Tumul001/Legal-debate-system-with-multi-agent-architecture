"""Tests for the debate orchestrator."""

import pytest
from src.core.orchestrator import DebateOrchestrator
from src.core.messages import AgentMessage, DebateResult, AgentRole
from src.utils.llm_client import LLMClient, MockLLM


def test_orchestrator_initialization():
    """Test that orchestrator initializes correctly."""
    orchestrator = DebateOrchestrator()
    assert orchestrator.max_rounds == 3
    assert orchestrator.current_round == 0
    assert orchestrator.topic == ""
    assert len(orchestrator.messages) == 0


def test_start_debate():
    """Test starting a debate."""
    orchestrator = DebateOrchestrator()
    topic = "Should jaywalking be a criminal offense?"

    orchestrator.start_debate(topic)

    assert orchestrator.topic == topic
    assert orchestrator.current_round == 0
    assert len(orchestrator.messages) == 0
    assert AgentRole.PROSECUTION in orchestrator.agents
    assert AgentRole.DEFENSE in orchestrator.agents


def test_debate_step():
    """Test a single debate step."""
    orchestrator = DebateOrchestrator()
    topic = "Test legal case"

    orchestrator.start_debate(topic)
    messages = orchestrator.step()

    assert len(messages) == 2
    assert messages[0].role == AgentRole.PROSECUTION
    assert messages[1].role == AgentRole.DEFENSE
    assert messages[0].round_number == 1
    assert messages[1].round_number == 1
    assert orchestrator.current_round == 1


def test_full_debate_with_mock_llm():
    """Test a complete debate using MockLLM."""
    orchestrator = DebateOrchestrator(max_rounds=2)
    topic = "Criminal case: defendant charged with theft"

    orchestrator.start_debate(topic)

    # Run 2 rounds
    round1_messages = orchestrator.step()
    assert len(round1_messages) == 2
    assert orchestrator.current_round == 1

    round2_messages = orchestrator.step()
    assert len(round2_messages) == 2
    assert orchestrator.current_round == 2

    # Evaluate
    result = orchestrator.evaluate()

    # Verify result structure
    assert isinstance(result, DebateResult)
    assert result.topic == topic
    assert len(result.messages) == 5  # 2 rounds × 2 agents + 1 judge
    assert result.winner in [AgentRole.PROSECUTION, AgentRole.DEFENSE, None]
    assert result.judge_reasoning != ""
    assert "prosecution" in result.scores
    assert "defense" in result.scores


def test_deterministic_mock_responses():
    """Test that MockLLM returns deterministic responses."""
    orchestrator1 = DebateOrchestrator(max_rounds=1)
    orchestrator2 = DebateOrchestrator(max_rounds=1)

    topic = "Test case"

    # Run two identical debates
    orchestrator1.start_debate(topic)
    orchestrator1.step()
    result1 = orchestrator1.evaluate()

    orchestrator2.start_debate(topic)
    orchestrator2.step()
    result2 = orchestrator2.evaluate()

    # Results should be identical
    assert result1.winner == result2.winner
    assert result1.scores == result2.scores
    assert len(result1.messages) == len(result2.messages)


def test_message_filtering():
    """Test filtering messages by role and round."""
    orchestrator = DebateOrchestrator(max_rounds=2)
    orchestrator.start_debate("Test topic")

    orchestrator.step()
    orchestrator.step()
    result = orchestrator.evaluate()

    # Get prosecution messages
    prosecution_msgs = result.get_messages_by_role(AgentRole.PROSECUTION)
    assert len(prosecution_msgs) == 2
    assert all(msg.role == AgentRole.PROSECUTION for msg in prosecution_msgs)

    # Get defense messages
    defense_msgs = result.get_messages_by_role(AgentRole.DEFENSE)
    assert len(defense_msgs) == 2
    assert all(msg.role == AgentRole.DEFENSE for msg in defense_msgs)

    # Get round 1 messages
    round1_msgs = result.get_messages_by_round(1)
    assert len(round1_msgs) == 2
    assert all(msg.round_number == 1 for msg in round1_msgs)


def test_max_rounds_limit():
    """Test that debate respects max_rounds limit."""
    orchestrator = DebateOrchestrator(max_rounds=2)
    orchestrator.start_debate("Test topic")

    # Should return messages for rounds 1 and 2
    orchestrator.step()
    orchestrator.step()

    # Should return empty list after max_rounds
    messages = orchestrator.step()
    assert len(messages) == 0
    assert orchestrator.current_round == 2


def test_get_state():
    """Test getting orchestrator state."""
    orchestrator = DebateOrchestrator(max_rounds=3)
    topic = "Legal debate topic"
    orchestrator.start_debate(topic)
    orchestrator.step()

    state = orchestrator.get_state()

    assert state["topic"] == topic
    assert state["current_round"] == 1
    assert state["max_rounds"] == 3
    assert state["message_count"] == 2
    assert "prosecution" in state["agents"]
    assert "defense" in state["agents"]


def test_llm_client_modes():
    """Test LLMClient initialization with different modes."""
    import os

    # Test mock mode
    os.environ["MOCK_LLM"] = "true"
    client = LLMClient()
    assert client.is_mock is True

    # Test without API key
    os.environ["MOCK_LLM"] = "false"
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    client = LLMClient()
    assert client.is_mock is True

    # Cleanup
    if "MOCK_LLM" in os.environ:
        del os.environ["MOCK_LLM"]


def test_agent_message_repr():
    """Test AgentMessage string representation."""
    msg = AgentMessage(
        role=AgentRole.PROSECUTION, content="This is a test message", round_number=1
    )

    repr_str = repr(msg)
    assert "prosecution" in repr_str
    assert "round=1" in repr_str
    assert "content_len=" in repr_str


def test_debate_result_repr():
    """Test DebateResult string representation."""
    result = DebateResult(topic="Test topic", messages=[], winner=AgentRole.PROSECUTION)

    repr_str = repr(result)
    assert "Test topic" in repr_str
    assert "prosecution" in repr_str
    assert "messages=0" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
