"""Core business logic for the legal debate system."""

from .messages import AgentMessage, DebateResult, LegalArgument, LegalCitation
from .orchestrator import DebateOrchestrator

__all__ = [
    "AgentMessage",
    "DebateResult",
    "LegalCitation",
    "LegalArgument",
    "DebateOrchestrator",
]
