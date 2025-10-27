"""
Debate orchestration and workflow management.

This module contains the DebateOrchestrator class that encapsulates the debate
flow, including starting debates, managing rounds, and evaluating results.
"""

from typing import Any, Callable, List, Optional

from .messages import DebateResult, LegalArgument


class DebateOrchestrator:
    """Orchestrates multi-agent legal debates.

    This class manages the flow of a legal debate between prosecution and
    defense agents, moderated by a neutral moderator. It handles round
    management, agent coordination, and result compilation.

    Attributes:
        max_rounds: Maximum number of debate rounds
        case_description: Description of the case being debated
        prosecution_arguments: List of prosecution arguments
        defense_arguments: List of defense arguments
        moderator_summaries: List of moderator summaries for each round
        current_round: Current round number
        debate_graph: The LangGraph workflow (if using LangGraph)
    """

    def __init__(self, max_rounds: int = 3, debate_graph: Optional[Any] = None):
        """Initialize the debate orchestrator.

        Args:
            max_rounds: Maximum number of rounds for the debate
            debate_graph: Optional LangGraph workflow for orchestration
        """
        self.max_rounds = max_rounds
        self.debate_graph = debate_graph
        self.case_description: str = ""
        self.prosecution_arguments: List[LegalArgument] = []
        self.defense_arguments: List[LegalArgument] = []
        self.moderator_summaries: List[str] = []
        self.current_round: int = 0
        self.final_judgement: str = ""

    def start_debate(
        self, case_description: str, progress_callback: Optional[Callable[[str], None]] = None
    ) -> DebateResult:
        """Start a new legal debate.

        This method initiates a complete debate workflow, managing all rounds
        of arguments and counter-arguments between prosecution and defense,
        with moderator evaluation.

        Args:
            case_description: Description of the legal case to debate
            progress_callback: Optional callback function for progress updates

        Returns:
            DebateResult containing all arguments and the final judgement

        Example:
            >>> orchestrator = DebateOrchestrator(max_rounds=3)
            >>> result = orchestrator.start_debate(
            ...     "Defendant charged with theft of property..."
            ... )
            >>> print(result.final_judgement)
        """
        self.case_description = case_description
        self.prosecution_arguments = []
        self.defense_arguments = []
        self.moderator_summaries = []
        self.current_round = 0
        self.final_judgement = ""

        if progress_callback:
            progress_callback(f"Starting debate for case: {case_description[:100]}...")

        # If using LangGraph workflow
        if self.debate_graph:
            initial_state = {
                "case_description": case_description,
                "prosecution_arguments": [],
                "defense_arguments": [],
                "debate_round": 1,
                "moderator_summary": "",
                "final_judgement": "",
                "case_citations_pool": [],
            }

            final_state = self.debate_graph.invoke(initial_state)

            # Extract results from final state
            self.prosecution_arguments = final_state.get("prosecution_arguments", [])
            self.defense_arguments = final_state.get("defense_arguments", [])
            self.moderator_summaries = [final_state.get("moderator_summary", "")]
            self.final_judgement = final_state.get("final_judgement", "")
            self.current_round = final_state.get("debate_round", 0)
        else:
            # Manual step-by-step debate (minimal implementation)
            for round_num in range(1, self.max_rounds + 1):
                self.current_round = round_num

                if progress_callback:
                    progress_callback(f"Round {round_num} starting...")

                # This would call agents to generate arguments
                # Minimal implementation - actual logic would be more complex
                pass

        return self.evaluate()

    def step(self, agent_role: str) -> Optional[LegalArgument]:
        """Execute one step of the debate (one agent's turn).

        Args:
            agent_role: The role of the agent to execute ('prosecution', 'defense', 'moderator')

        Returns:
            LegalArgument if applicable, None for moderator steps

        Example:
            >>> orchestrator = DebateOrchestrator()
            >>> orchestrator.case_description = "Sample case..."
            >>> argument = orchestrator.step('prosecution')
        """
        # Minimal implementation - actual implementation would invoke agents
        if agent_role == "prosecution":
            # Would generate prosecution argument here
            return None
        elif agent_role == "defense":
            # Would generate defense argument here
            return None
        elif agent_role == "moderator":
            # Would generate moderator summary here
            return None

        return None

    def evaluate(self) -> DebateResult:
        """Evaluate the complete debate and generate results.

        This method compiles all arguments, summaries, and generates a final
        judgement based on the debate proceedings.

        Returns:
            DebateResult containing the complete debate record

        Example:
            >>> result = orchestrator.evaluate()
            >>> print(f"Total rounds: {result.total_rounds}")
            >>> print(f"Citations used: {len(result.all_citations)}")
        """
        result = DebateResult(
            case_description=self.case_description,
            prosecution_arguments=self.prosecution_arguments,
            defense_arguments=self.defense_arguments,
            moderator_summaries=self.moderator_summaries,
            final_judgement=self.final_judgement,
            total_rounds=self.current_round,
        )

        # Extract all citations
        result.all_citations = result.get_all_citations()

        return result

    def get_state(self) -> dict:
        """Get the current state of the debate.

        Returns:
            Dictionary containing current debate state
        """
        return {
            "case_description": self.case_description,
            "prosecution_arguments": self.prosecution_arguments,
            "defense_arguments": self.defense_arguments,
            "moderator_summaries": self.moderator_summaries,
            "current_round": self.current_round,
            "final_judgement": self.final_judgement,
        }

    def reset(self):
        """Reset the orchestrator to initial state."""
        self.case_description = ""
        self.prosecution_arguments = []
        self.defense_arguments = []
        self.moderator_summaries = []
        self.current_round = 0
        self.final_judgement = ""
