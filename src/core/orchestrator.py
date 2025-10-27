"""Debate orchestrator for managing multi-agent debates."""

from typing import List, Optional, Dict
from .messages import AgentMessage, DebateResult, AgentRole
from ..utils.llm_client import LLMClient


class DebateOrchestrator:
    """
    Orchestrates a structured debate between prosecution and defense agents.

    The orchestrator manages:
    - Debate initialization with topic and agents
    - Turn-by-turn debate rounds
    - Judge evaluation and scoring
    - Final result compilation
    """

    def __init__(self, llm_client: Optional[LLMClient] = None, max_rounds: int = 3):
        """
        Initialize the debate orchestrator.

        Args:
            llm_client: LLM client for generating responses. Creates MockLLM if None.
            max_rounds: Maximum number of debate rounds (default: 3)
        """
        self.llm_client = llm_client or LLMClient()
        self.max_rounds = max_rounds
        self.current_round = 0
        self.topic = ""
        self.messages: List[AgentMessage] = []
        self.agents: Dict[AgentRole, str] = {}

    def start_debate(
        self, topic: str, agents: Optional[Dict[AgentRole, str]] = None
    ) -> None:
        """
        Initialize a new debate with the given topic.

        Args:
            topic: The debate topic or case description
            agents: Optional dictionary mapping roles to agent descriptions
        """
        self.topic = topic
        self.current_round = 0
        self.messages = []

        # Set default agent descriptions if not provided
        if agents is None:
            self.agents = {
                AgentRole.PROSECUTION: "prosecution attorney",
                AgentRole.DEFENSE: "defense attorney",
                AgentRole.JUDGE: "impartial judge",
            }
        else:
            self.agents = agents

    def step(self) -> List[AgentMessage]:
        """
        Execute one round of the debate.

        In each round:
        1. Prosecution presents argument
        2. Defense responds
        3. Both messages are added to the debate history

        Returns:
            List of messages generated in this round
        """
        if self.current_round >= self.max_rounds:
            return []

        self.current_round += 1
        round_messages = []

        # Prosecution argument
        prosecution_prompt = self._build_prosecution_prompt()
        prosecution_response = self.llm_client.generate(prosecution_prompt)
        prosecution_msg = AgentMessage(
            role=AgentRole.PROSECUTION,
            content=prosecution_response,
            round_number=self.current_round,
            metadata={
                "agent_type": self.agents.get(AgentRole.PROSECUTION, "prosecution")
            },
        )
        self.messages.append(prosecution_msg)
        round_messages.append(prosecution_msg)

        # Defense response
        defense_prompt = self._build_defense_prompt()
        defense_response = self.llm_client.generate(defense_prompt)
        defense_msg = AgentMessage(
            role=AgentRole.DEFENSE,
            content=defense_response,
            round_number=self.current_round,
            metadata={"agent_type": self.agents.get(AgentRole.DEFENSE, "defense")},
        )
        self.messages.append(defense_msg)
        round_messages.append(defense_msg)

        return round_messages

    def evaluate(self) -> DebateResult:
        """
        Have the judge evaluate the debate and determine the outcome.

        Returns:
            DebateResult containing all messages, scores, winner, and reasoning
        """
        # Build judge evaluation prompt
        judge_prompt = self._build_judge_prompt()
        judge_response = self.llm_client.generate(judge_prompt)

        # Create judge message
        judge_msg = AgentMessage(
            role=AgentRole.JUDGE,
            content=judge_response,
            round_number=self.current_round,
            metadata={"agent_type": self.agents.get(AgentRole.JUDGE, "judge")},
        )
        self.messages.append(judge_msg)

        # Parse scores and winner from judge response
        scores, winner = self._parse_judge_decision(judge_response)

        # Create and return debate result
        result = DebateResult(
            topic=self.topic,
            messages=self.messages.copy(),
            winner=winner,
            judge_reasoning=judge_response,
            scores=scores,
            metadata={
                "rounds": self.current_round,
                "max_rounds": self.max_rounds,
                "llm_mode": self.llm_client.get_status().get("mode", "unknown"),
            },
        )

        return result

    def _build_prosecution_prompt(self) -> str:
        """Build prompt for prosecution argument."""
        context = self._get_debate_context()
        return f"""You are the prosecution attorney in a legal debate.

Topic: {self.topic}

{context}

Round {self.current_round} of {self.max_rounds}: Present your argument for the prosecution.
Be clear, logical, and cite relevant legal principles."""

    def _build_defense_prompt(self) -> str:
        """Build prompt for defense response."""
        context = self._get_debate_context()

        # Get the latest prosecution argument
        prosecution_msgs = [m for m in self.messages if m.role == AgentRole.PROSECUTION]
        latest_prosecution = prosecution_msgs[-1].content if prosecution_msgs else ""

        return f"""You are the defense attorney in a legal debate.

Topic: {self.topic}

{context}

The prosecution just argued: {latest_prosecution}

Round {self.current_round} of {self.max_rounds}: Present your defense and respond to the prosecution's arguments.
Be clear, logical, and cite relevant legal principles."""

    def _build_judge_prompt(self) -> str:
        """Build prompt for judge evaluation."""
        context = self._get_debate_context()
        return f"""You are an impartial judge evaluating a legal debate.

Topic: {self.topic}

{context}

Evaluate both sides' arguments. Provide:
1. Score for prosecution (0-10)
2. Score for defense (0-10)
3. Your reasoning
4. Your decision on which side presented the stronger case

Format your response to include "Prosecution score: X/10" and "Defense score: Y/10"."""

    def _get_debate_context(self) -> str:
        """Get a summary of the debate so far."""
        if not self.messages:
            return "This is the start of the debate."

        context_parts = []
        for i in range(1, self.current_round + 1):
            round_msgs = [m for m in self.messages if m.round_number == i]
            if round_msgs:
                context_parts.append(f"\n--- Round {i} ---")
                for msg in round_msgs:
                    context_parts.append(
                        f"{msg.role.value.upper()}: {msg.content[:200]}..."
                    )

        return (
            "\n".join(context_parts)
            if context_parts
            else "Previous arguments have been presented."
        )

    def _parse_judge_decision(
        self, judge_response: str
    ) -> tuple[Dict[str, int], Optional[AgentRole]]:
        """
        Parse the judge's response to extract scores and winner.

        Args:
            judge_response: The judge's evaluation text

        Returns:
            Tuple of (scores dict, winner AgentRole)
        """
        scores = {"prosecution": 0, "defense": 0}
        winner = None

        # Parse scores from response
        response_lower = judge_response.lower()

        # Try to find prosecution score
        if "prosecution score:" in response_lower or "prosecution:" in response_lower:
            try:
                # Find the score after "prosecution score:"
                start_idx = response_lower.find("prosecution")
                section = judge_response[start_idx : start_idx + 50]
                for word in section.split():
                    if "/" in word:
                        score = int(word.split("/")[0])
                        scores["prosecution"] = score
                        break
            except (ValueError, IndexError):
                scores["prosecution"] = 5  # Default

        # Try to find defense score
        if "defense score:" in response_lower or "defense:" in response_lower:
            try:
                start_idx = response_lower.find("defense")
                section = judge_response[start_idx : start_idx + 50]
                for word in section.split():
                    if "/" in word:
                        score = int(word.split("/")[0])
                        scores["defense"] = score
                        break
            except (ValueError, IndexError):
                scores["defense"] = 5  # Default

        # Determine winner based on scores
        if scores["prosecution"] > scores["defense"]:
            winner = AgentRole.PROSECUTION
        elif scores["defense"] > scores["prosecution"]:
            winner = AgentRole.DEFENSE
        # If tied, winner remains None

        return scores, winner

    def get_state(self) -> Dict:
        """
        Get the current state of the debate.

        Returns:
            Dictionary containing current debate state
        """
        return {
            "topic": self.topic,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "message_count": len(self.messages),
            "agents": {role.value: desc for role, desc in self.agents.items()},
        }
