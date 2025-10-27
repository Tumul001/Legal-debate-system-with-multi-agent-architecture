"""Data structures for debate messages and results."""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class AgentRole(str, Enum):
    """Enum for agent roles in the debate."""

    PROSECUTION = "prosecution"
    DEFENSE = "defense"
    JUDGE = "judge"


@dataclass
class AgentMessage:
    """
    Represents a message from an agent in the debate.

    Attributes:
        role: The role of the agent (prosecution, defense, or judge)
        content: The text content of the message
        round_number: The debate round this message belongs to
        metadata: Optional metadata dictionary for additional information
    """

    role: AgentRole
    content: str
    round_number: int
    metadata: Optional[dict] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a readable string representation."""
        return (
            f"AgentMessage(role={self.role.value}, "
            f"round={self.round_number}, "
            f"content_len={len(self.content)})"
        )


@dataclass
class DebateResult:
    """
    Represents the final result of a debate.

    Attributes:
        topic: The debate topic
        messages: List of all messages exchanged during the debate
        winner: The winning side (prosecution or defense), if determined
        judge_reasoning: The judge's final reasoning
        scores: Optional scores for each side
        metadata: Optional metadata dictionary for additional information
    """

    topic: str
    messages: List[AgentMessage] = field(default_factory=list)
    winner: Optional[AgentRole] = None
    judge_reasoning: str = ""
    scores: Optional[dict] = field(default_factory=dict)
    metadata: Optional[dict] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return a readable string representation."""
        winner_str = self.winner.value if self.winner else "undecided"
        return (
            f"DebateResult(topic='{self.topic[:50]}...', "
            f"messages={len(self.messages)}, "
            f"winner={winner_str})"
        )

    def get_messages_by_role(self, role: AgentRole) -> List[AgentMessage]:
        """Get all messages from a specific role."""
        return [msg for msg in self.messages if msg.role == role]

    def get_messages_by_round(self, round_number: int) -> List[AgentMessage]:
        """Get all messages from a specific round."""
        return [msg for msg in self.messages if msg.round_number == round_number]
