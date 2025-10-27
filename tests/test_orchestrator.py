"""
Tests for the DebateOrchestrator with deterministic MockLLM.

These tests verify debate flow using mock LLM responses.
"""

import json

import pytest

from src.core.messages import LegalArgument, LegalCitation
from src.core.orchestrator import DebateOrchestrator
from src.utils.llm_client import MockLLM


def test_orchestrator_evaluate_empty():
    """Test evaluate with no arguments."""
    orchestrator = DebateOrchestrator()
    orchestrator.case_description = "Test case"

    result = orchestrator.evaluate()

    assert result.case_description == "Test case"
    assert len(result.prosecution_arguments) == 0
    assert len(result.defense_arguments) == 0
    assert result.total_rounds == 0


def test_orchestrator_evaluate_with_arguments():
    """Test evaluate with mock arguments."""
    orchestrator = DebateOrchestrator()
    orchestrator.case_description = "Test case"
    orchestrator.current_round = 1

    # Add a mock argument
    citation = LegalCitation(
        case_name="Test v. State",
        year=2020,
        citation="123 F.3d 456",
        relevance="Test relevance",
        excerpt="Test excerpt",
    )

    argument = LegalArgument(
        position="prosecution",
        main_argument="Test main argument",
        supporting_points=["Point 1", "Point 2"],
        case_citations=[citation],
        statutes_cited=["Test Statute"],
        confidence_score=0.75,
        weaknesses_acknowledged=["Weakness 1"],
        legal_reasoning="Test reasoning",
    )

    orchestrator.prosecution_arguments.append(argument)
    orchestrator.final_judgement = "Test judgement"

    result = orchestrator.evaluate()

    assert result.case_description == "Test case"
    assert len(result.prosecution_arguments) == 1
    assert result.total_rounds == 1
    assert result.final_judgement == "Test judgement"
    assert len(result.all_citations) == 1


def test_orchestrator_step_prosecution():
    """Test orchestrator step for prosecution."""
    orchestrator = DebateOrchestrator()
    orchestrator.case_description = "Test case"

    # Step should return None in minimal implementation
    result = orchestrator.step("prosecution")

    assert result is None


def test_orchestrator_step_defense():
    """Test orchestrator step for defense."""
    orchestrator = DebateOrchestrator()
    orchestrator.case_description = "Test case"

    # Step should return None in minimal implementation
    result = orchestrator.step("defense")

    assert result is None


def test_orchestrator_step_moderator():
    """Test orchestrator step for moderator."""
    orchestrator = DebateOrchestrator()
    orchestrator.case_description = "Test case"

    # Step should return None in minimal implementation
    result = orchestrator.step("moderator")

    assert result is None


def test_mock_llm_json_responses():
    """Test that MockLLM returns valid JSON for legal arguments."""
    mock_llm = MockLLM()

    # First response should be prosecution argument
    response = mock_llm.invoke([])

    # Should be valid JSON
    try:
        data = json.loads(response.content)
        assert "position" in data
        assert "main_argument" in data
        assert "confidence_score" in data
    except json.JSONDecodeError:
        pytest.fail("MockLLM did not return valid JSON")


def test_mock_llm_alternating_roles():
    """Test that MockLLM alternates between prosecution and defense."""
    mock_llm = MockLLM()

    # First should be prosecution
    response1 = mock_llm.invoke([])
    data1 = json.loads(response1.content)
    assert data1["position"] == "prosecution"

    # Second should be defense
    response2 = mock_llm.invoke([])
    data2 = json.loads(response2.content)
    assert data2["position"] == "defense"


def test_orchestrator_with_debate_graph():
    """Test orchestrator with a mock debate graph."""

    # Mock debate graph
    class MockDebateGraph:
        def invoke(self, state):
            # Return a simple state with one argument
            citation = LegalCitation(
                case_name="Mock v. State",
                year=2020,
                citation="123 F.3d 456",
                relevance="Mock relevance",
                excerpt="Mock excerpt",
            )

            argument = LegalArgument(
                position="prosecution",
                main_argument="Mock argument",
                supporting_points=["Point 1"],
                case_citations=[citation],
                statutes_cited=["Mock Statute"],
                confidence_score=0.80,
                weaknesses_acknowledged=["Weakness"],
                legal_reasoning="Mock reasoning",
            )

            return {
                "case_description": state["case_description"],
                "prosecution_arguments": [argument],
                "defense_arguments": [],
                "debate_round": 1,
                "moderator_summary": "Mock summary",
                "final_judgement": "Mock judgement",
                "case_citations_pool": [],
            }

    mock_graph = MockDebateGraph()
    orchestrator = DebateOrchestrator(max_rounds=3, debate_graph=mock_graph)

    result = orchestrator.start_debate("Test case description")

    assert result.case_description == "Test case description"
    assert len(result.prosecution_arguments) == 1
    assert result.prosecution_arguments[0].main_argument == "Mock argument"
    assert result.final_judgement == "Mock judgement"


def test_orchestrator_progress_callback():
    """Test orchestrator with progress callback."""
    messages = []

    def progress_callback(msg):
        messages.append(msg)

    orchestrator = DebateOrchestrator(max_rounds=3)
    orchestrator.start_debate("Test case", progress_callback=progress_callback)

    # Should have received at least one progress message
    assert len(messages) > 0
    assert "Test case" in messages[0]


def test_orchestrator_multiple_rounds():
    """Test orchestrator evaluation with multiple rounds of arguments."""
    orchestrator = DebateOrchestrator(max_rounds=3)
    orchestrator.case_description = "Multi-round test case"
    orchestrator.current_round = 3

    # Add multiple prosecution arguments
    for i in range(3):
        citation = LegalCitation(
            case_name=f"Test{i} v. State",
            year=2020 + i,
            citation=f"{100+i} F.3d {200+i}",
            relevance=f"Relevance {i}",
            excerpt=f"Excerpt {i}",
        )

        argument = LegalArgument(
            position="prosecution",
            main_argument=f"Argument {i}",
            supporting_points=[f"Point {i}"],
            case_citations=[citation],
            statutes_cited=[f"Statute {i}"],
            confidence_score=0.70 + i * 0.05,
            weaknesses_acknowledged=[f"Weakness {i}"],
            legal_reasoning=f"Reasoning {i}",
        )
        orchestrator.prosecution_arguments.append(argument)

    # Add multiple defense arguments
    for i in range(3):
        citation = LegalCitation(
            case_name=f"Defense{i} v. State",
            year=2020 + i,
            citation=f"{300+i} F.3d {400+i}",
            relevance=f"Defense Relevance {i}",
            excerpt=f"Defense Excerpt {i}",
        )

        argument = LegalArgument(
            position="defense",
            main_argument=f"Defense Argument {i}",
            supporting_points=[f"Defense Point {i}"],
            case_citations=[citation],
            statutes_cited=[f"Defense Statute {i}"],
            confidence_score=0.65 + i * 0.05,
            weaknesses_acknowledged=[f"Defense Weakness {i}"],
            legal_reasoning=f"Defense Reasoning {i}",
        )
        orchestrator.defense_arguments.append(argument)

    orchestrator.moderator_summaries = [f"Summary Round {i}" for i in range(3)]
    orchestrator.final_judgement = "Final multi-round judgement"

    result = orchestrator.evaluate()

    assert len(result.prosecution_arguments) == 3
    assert len(result.defense_arguments) == 3
    assert len(result.moderator_summaries) == 3
    assert result.total_rounds == 3

    # Check that all unique citations are collected
    all_citations = result.get_all_citations()
    assert len(all_citations) == 6  # 3 prosecution + 3 defense

    # Verify citation names
    citation_names = [c.case_name for c in all_citations]
    assert "Test0 v. State" in citation_names
    assert "Defense0 v. State" in citation_names
