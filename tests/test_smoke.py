"""
Smoke tests for the legal debate system.

These tests verify basic functionality without requiring external API calls.
"""

import pytest
from src.core.messages import AgentMessage, DebateResult, LegalCitation, LegalArgument
from src.core.orchestrator import DebateOrchestrator
from src.utils.llm_client import MockLLM


def test_agent_message_creation():
    """Test creating an AgentMessage."""
    message = AgentMessage(
        role="prosecution",
        content="Test argument",
        round_number=1,
        metadata={"test": "value"}
    )
    
    assert message.role == "prosecution"
    assert message.content == "Test argument"
    assert message.round_number == 1
    assert message.metadata["test"] == "value"


def test_legal_citation_creation():
    """Test creating a LegalCitation."""
    citation = LegalCitation(
        case_name="Test v. State",
        year=2020,
        citation="123 F.3d 456",
        relevance="Test relevance",
        excerpt="Test excerpt"
    )
    
    assert citation.case_name == "Test v. State"
    assert citation.year == 2020
    assert citation.citation == "123 F.3d 456"


def test_legal_argument_creation():
    """Test creating a LegalArgument."""
    citation = LegalCitation(
        case_name="Test v. State",
        year=2020,
        citation="123 F.3d 456",
        relevance="Test relevance",
        excerpt="Test excerpt"
    )
    
    argument = LegalArgument(
        position="prosecution",
        main_argument="Test main argument",
        supporting_points=["Point 1", "Point 2"],
        case_citations=[citation],
        statutes_cited=["Test Statute"],
        confidence_score=0.75,
        weaknesses_acknowledged=["Weakness 1"],
        legal_reasoning="Test reasoning"
    )
    
    assert argument.position == "prosecution"
    assert argument.main_argument == "Test main argument"
    assert len(argument.supporting_points) == 2
    assert len(argument.case_citations) == 1
    assert argument.confidence_score == 0.75


def test_debate_result_creation():
    """Test creating a DebateResult."""
    citation = LegalCitation(
        case_name="Test v. State",
        year=2020,
        citation="123 F.3d 456",
        relevance="Test relevance",
        excerpt="Test excerpt"
    )
    
    argument = LegalArgument(
        position="prosecution",
        main_argument="Test main argument",
        supporting_points=["Point 1"],
        case_citations=[citation],
        statutes_cited=["Test Statute"],
        confidence_score=0.75,
        weaknesses_acknowledged=["Weakness 1"],
        legal_reasoning="Test reasoning"
    )
    
    result = DebateResult(
        case_description="Test case",
        prosecution_arguments=[argument],
        defense_arguments=[],
        moderator_summaries=["Test summary"],
        final_judgement="Test judgement",
        total_rounds=1
    )
    
    assert result.case_description == "Test case"
    assert len(result.prosecution_arguments) == 1
    assert result.total_rounds == 1


def test_debate_result_get_all_citations():
    """Test extracting all citations from a debate result."""
    citation1 = LegalCitation(
        case_name="Test v. State",
        year=2020,
        citation="123 F.3d 456",
        relevance="Test relevance",
        excerpt="Test excerpt"
    )
    
    citation2 = LegalCitation(
        case_name="Another v. State",
        year=2021,
        citation="456 F.3d 789",
        relevance="Test relevance 2",
        excerpt="Test excerpt 2"
    )
    
    argument1 = LegalArgument(
        position="prosecution",
        main_argument="Test main argument",
        supporting_points=["Point 1"],
        case_citations=[citation1],
        statutes_cited=["Test Statute"],
        confidence_score=0.75,
        weaknesses_acknowledged=["Weakness 1"],
        legal_reasoning="Test reasoning"
    )
    
    argument2 = LegalArgument(
        position="defense",
        main_argument="Test defense argument",
        supporting_points=["Point 1"],
        case_citations=[citation2],
        statutes_cited=["Test Statute"],
        confidence_score=0.70,
        weaknesses_acknowledged=["Weakness 1"],
        legal_reasoning="Test reasoning"
    )
    
    result = DebateResult(
        case_description="Test case",
        prosecution_arguments=[argument1],
        defense_arguments=[argument2],
        moderator_summaries=["Test summary"],
        final_judgement="Test judgement",
        total_rounds=1
    )
    
    citations = result.get_all_citations()
    assert len(citations) == 2
    assert citations[0].case_name == "Test v. State"
    assert citations[1].case_name == "Another v. State"


def test_mock_llm_basic():
    """Test basic MockLLM functionality."""
    mock_llm = MockLLM()
    
    response = mock_llm.invoke([])
    assert response.content is not None
    assert len(response.content) > 0
    
    # Check call count increments
    assert mock_llm.call_count == 1
    
    mock_llm.invoke([])
    assert mock_llm.call_count == 2


def test_mock_llm_custom_responses():
    """Test MockLLM with custom responses."""
    custom_responses = ["Response 1", "Response 2", "Response 3"]
    mock_llm = MockLLM(responses=custom_responses)
    
    # Should cycle through responses
    response1 = mock_llm.invoke([])
    assert response1.content == "Response 1"
    
    response2 = mock_llm.invoke([])
    assert response2.content == "Response 2"
    
    response3 = mock_llm.invoke([])
    assert response3.content == "Response 3"
    
    # Should cycle back to the first
    response4 = mock_llm.invoke([])
    assert response4.content == "Response 1"


def test_mock_llm_reset():
    """Test MockLLM reset functionality."""
    mock_llm = MockLLM()
    
    mock_llm.invoke([])
    mock_llm.invoke([])
    assert mock_llm.call_count == 2
    
    mock_llm.reset()
    assert mock_llm.call_count == 0


def test_orchestrator_initialization():
    """Test DebateOrchestrator initialization."""
    orchestrator = DebateOrchestrator(max_rounds=3)
    
    assert orchestrator.max_rounds == 3
    assert orchestrator.current_round == 0
    assert len(orchestrator.prosecution_arguments) == 0
    assert len(orchestrator.defense_arguments) == 0


def test_orchestrator_reset():
    """Test DebateOrchestrator reset."""
    orchestrator = DebateOrchestrator(max_rounds=3)
    orchestrator.case_description = "Test case"
    orchestrator.current_round = 2
    
    orchestrator.reset()
    
    assert orchestrator.case_description == ""
    assert orchestrator.current_round == 0
    assert len(orchestrator.prosecution_arguments) == 0


def test_orchestrator_get_state():
    """Test DebateOrchestrator state retrieval."""
    orchestrator = DebateOrchestrator(max_rounds=3)
    orchestrator.case_description = "Test case"
    orchestrator.current_round = 1
    
    state = orchestrator.get_state()
    
    assert state["case_description"] == "Test case"
    assert state["current_round"] == 1
    assert isinstance(state["prosecution_arguments"], list)
    assert isinstance(state["defense_arguments"], list)
