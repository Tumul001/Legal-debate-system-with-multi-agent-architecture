"""LLM client implementations including mock for testing."""

import os
from typing import Optional, Dict
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        pass


class MockLLM(BaseLLM):
    """
    Deterministic mock LLM for testing.

    Returns predictable responses based on the role detected in the prompt.
    """

    def __init__(self):
        """Initialize the mock LLM."""
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a deterministic response based on prompt content.

        Args:
            prompt: The input prompt
            **kwargs: Ignored for mock implementation

        Returns:
            Deterministic response based on detected role
        """
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Detect role from prompt
        if "prosecution" in prompt_lower or "prosecute" in prompt_lower:
            return self._get_prosecution_response(self.call_count)
        elif "defense" in prompt_lower or "defend" in prompt_lower:
            return self._get_defense_response(self.call_count)
        elif (
            "judge" in prompt_lower
            or "evaluate" in prompt_lower
            or "score" in prompt_lower
        ):
            return self._get_judge_response(self.call_count)
        else:
            return f"Mock response {self.call_count}: {prompt[:50]}"

    def _get_prosecution_response(self, call_num: int) -> str:
        """Get prosecution response."""
        responses = [
            "The prosecution argues that the evidence clearly demonstrates guilt. "
            "The defendant's actions violated statutory law, and precedent supports conviction.",
            "In response to the defense, the prosecution maintains that the evidence "
            "is overwhelming and meets the burden of proof beyond reasonable doubt.",
            "The prosecution reiterates that all legal standards have been met and "
            "requests the court find the defendant guilty as charged.",
        ]
        return responses[(call_num - 1) % len(responses)]

    def _get_defense_response(self, call_num: int) -> str:
        """Get defense response."""
        responses = [
            "The defense contends that the evidence is insufficient and circumstantial. "
            "The defendant's constitutional rights must be protected, and reasonable doubt exists.",
            "The defense counters that the prosecution has failed to meet its burden. "
            "Precedent and statutory interpretation favor the defendant's position.",
            "The defense concludes that the facts do not support conviction and "
            "respectfully requests the court find the defendant not guilty.",
        ]
        return responses[(call_num - 1) % len(responses)]

    def _get_judge_response(self, call_num: int) -> str:
        """Get judge response."""
        responses = [
            "After careful consideration of both arguments, the court finds merit in both sides. "
            "Prosecution score: 7/10. Defense score: 6/10. The debate shall continue.",
            "The court has evaluated the arguments presented. "
            "Prosecution score: 6/10. Defense score: 7/10. Further deliberation is needed.",
            "Based on the totality of arguments, the court finds in favor of the prosecution. "
            "Prosecution score: 8/10. Defense score: 6/10. The prosecution presents the stronger case.",
        ]
        return responses[(call_num - 1) % len(responses)]


class LLMClient:
    """
    LLM client that uses OpenAI API or MockLLM.

    Uses MockLLM when:
    - OPENAI_API_KEY environment variable is not set
    - MOCK_LLM environment variable is set to 'true'

    Otherwise uses OpenAI API.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenAI API key (reads from OPENAI_API_KEY env var if not provided)
            model: Model name to use
        """
        self.model = model
        self.use_mock = os.getenv("MOCK_LLM", "false").lower() == "true"

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Use mock if API key is missing or MOCK_LLM is true
        if not self.api_key or self.use_mock:
            self.llm = MockLLM()
            self.is_mock = True
        else:
            # In a real implementation, this would initialize OpenAI client
            # For now, we'll use mock as we don't want to make actual API calls
            self.llm = MockLLM()
            self.is_mock = True

    def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """
        Generate text using the underlying LLM.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if self.is_mock:
            return self.llm.generate(prompt)
        else:
            # Real OpenAI implementation would go here
            # from openai import OpenAI
            # client = OpenAI(api_key=self.api_key)
            # response = client.chat.completions.create(...)
            # return response.choices[0].message.content
            return self.llm.generate(prompt)

    def get_status(self) -> Dict[str, str]:
        """Get the current status of the LLM client."""
        return {
            "mode": "mock" if self.is_mock else "real",
            "model": self.model,
            "has_api_key": bool(self.api_key),
        }
