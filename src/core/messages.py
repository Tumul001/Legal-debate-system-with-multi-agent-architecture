"""
Typed dataclasses for legal debate messages and results.

This module defines the core data structures used throughout the legal debate
system, including agent messages, legal citations, and debate results.
"""

from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field


class LegalCitation(BaseModel):
    """Represents a single case law citation.
    
    Attributes:
        case_name: Name of the legal case
        year: Year of the decision
        citation: Official citation
        relevance: How this case applies to current argument
        excerpt: Key legal principle from the case
    """
    case_name: str = Field(description="Name of the legal case")
    year: int = Field(description="Year of the decision")
    citation: str = Field(description="Official citation")
    relevance: str = Field(description="How this case applies to current argument")
    excerpt: str = Field(description="Key legal principle from the case")


class LegalArgument(BaseModel):
    """Structured output for a legal agent's argument.
    
    Attributes:
        position: Either 'prosecution' or 'defense'
        main_argument: Core legal argument in 2-3 sentences
        supporting_points: 3-5 supporting arguments
        case_citations: Relevant case law citations
        statutes_cited: Relevant statutes or legal codes
        confidence_score: Confidence in argument strength (0.0-1.0)
        weaknesses_acknowledged: Potential counterarguments
        legal_reasoning: Detailed reasoning connecting facts to law
    """
    position: str = Field(description="Either 'prosecution' or 'defense'")
    main_argument: str = Field(description="Core legal argument in 2-3 sentences")
    supporting_points: List[str] = Field(description="3-5 supporting arguments")
    case_citations: List[LegalCitation] = Field(description="Relevant case law citations")
    statutes_cited: List[str] = Field(description="Relevant statutes or legal codes")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in argument strength")
    weaknesses_acknowledged: List[str] = Field(description="Potential counterarguments")
    legal_reasoning: str = Field(description="Detailed reasoning connecting facts to law")


@dataclass
class AgentMessage:
    """A message from a debate agent.
    
    Attributes:
        role: The role of the agent (prosecution, defense, moderator)
        content: The message content
        round_number: The debate round this message belongs to
        metadata: Additional metadata about the message
    """
    role: str
    content: str
    round_number: int
    metadata: dict = field(default_factory=dict)


@dataclass
class DebateResult:
    """The result of a complete debate.
    
    Attributes:
        case_description: The case that was debated
        prosecution_arguments: List of prosecution arguments across all rounds
        defense_arguments: List of defense arguments across all rounds
        moderator_summaries: List of moderator summaries for each round
        final_judgement: The final judgement from the moderator
        total_rounds: Total number of rounds completed
        all_citations: All case citations used in the debate
    """
    case_description: str
    prosecution_arguments: List[LegalArgument]
    defense_arguments: List[LegalArgument]
    moderator_summaries: List[str]
    final_judgement: str
    total_rounds: int
    all_citations: List[LegalCitation] = field(default_factory=list)
    
    def get_all_citations(self) -> List[LegalCitation]:
        """Extract all unique citations from the debate.
        
        Returns:
            List of unique LegalCitation objects
        """
        all_cites = []
        seen_cases = set()
        
        for arg in self.prosecution_arguments + self.defense_arguments:
            for citation in arg.case_citations:
                if citation.case_name not in seen_cases:
                    all_cites.append(citation)
                    seen_cases.add(citation.case_name)
        
        return all_cites
