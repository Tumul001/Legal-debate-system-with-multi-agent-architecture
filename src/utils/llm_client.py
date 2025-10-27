"""
LLM client wrapper with retry logic and mock implementations.

This module provides a wrapper for LLM calls with environment-based API key
loading, retry logic with exponential backoff, and a MockLLM class for
deterministic offline testing.
"""

import os
import time
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain.schema import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class LLMClient:
    """Wrapper for LLM calls with retry logic and API key management.

    This class provides a consistent interface for LLM interactions with
    built-in retry logic and environment-based configuration.

    Attributes:
        api_key: Google API key for Gemini
        model_name: Name of the model to use
        temperature: Sampling temperature for generation
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.3,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
    ):
        """Initialize the LLM client.

        Args:
            api_key: Google API key. If None, loads from GOOGLE_API_KEY env var
            model_name: Name of the Gemini model to use
            temperature: Temperature for generation (0.0-1.0)
            max_retries: Maximum number of retry attempts on failure
            initial_backoff: Initial backoff time in seconds for retries
        """
        # Load environment variables
        load_dotenv()

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be provided or set in environment variables")

        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

        # Initialize the LLM
        self._llm = ChatGoogleGenerativeAI(
            model=model_name, temperature=temperature, google_api_key=self.api_key
        )

    def invoke(self, messages: List[Any]) -> AIMessage:
        """Invoke the LLM with retry logic.

        Args:
            messages: List of messages to send to the LLM

        Returns:
            AIMessage response from the LLM

        Raises:
            Exception: If all retry attempts fail
        """
        backoff = self.initial_backoff
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = self._llm.invoke(messages)
                return response
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                else:
                    raise Exception(
                        f"Failed after {self.max_retries} attempts: {str(last_exception)}"
                    )

        # Should never reach here, but for type safety
        raise Exception(f"Unexpected error in retry logic: {str(last_exception)}")


class MockLLM:
    """Mock LLM for deterministic offline testing.

    This class provides a mock implementation of the LLM interface for testing
    purposes. It returns predictable, deterministic responses without making
    actual API calls.

    Attributes:
        responses: List of pre-defined responses to return
        call_count: Number of times invoke has been called
    """

    def __init__(self, responses: Optional[List[str]] = None):
        """Initialize the mock LLM.

        Args:
            responses: Optional list of responses to cycle through.
                      If None, uses default mock responses.
        """
        self.call_count = 0
        self.responses = responses or self._get_default_responses()

    def invoke(self, messages: List[Any]) -> AIMessage:
        """Return a mock response.

        Args:
            messages: Messages to send (ignored in mock)

        Returns:
            AIMessage with mock content
        """
        response_idx = self.call_count % len(self.responses)
        response_content = self.responses[response_idx]
        self.call_count += 1

        return AIMessage(content=response_content)

    def _get_default_responses(self) -> List[str]:
        """Get default mock responses for testing.

        Returns:
            List of JSON-formatted mock legal arguments
        """
        return [
            # Prosecution argument
            """{
                "position": "prosecution",
                "main_argument": "The defendant violated established legal """
            """principles by failing to comply with lawful orders.",
                "supporting_points": [
                    "Legal precedent supports strict interpretation of """
            """compliance requirements",
                    "The defendant had clear notice of their obligations",
                    "Similar cases have resulted in conviction"
                ],
                "case_citations": [
                    {
                        "case_name": "Test v. State",
                        "year": 2020,
                        "citation": "123 F.3d 456",
                        "relevance": "Establishes the standard for """
            """compliance",
                        "excerpt": "Defendants must demonstrate good """
            """faith compliance"
                    }
                ],
                "statutes_cited": ["18 U.S.C. § 1001"],
                "confidence_score": 0.75,
                "weaknesses_acknowledged": ["Defense may argue lack of """
            """intent"],
                "legal_reasoning": "The totality of circumstances """
            """demonstrates that the defendant's actions were knowing and """
            """willful, satisfying all elements of the offense."
            }""",
            # Defense argument
            """{
                "position": "defense",
                "main_argument": "The defendant acted in good faith and """
            """lacked the requisite intent for criminal liability.",
                "supporting_points": [
                    "No evidence of willful violation",
                    "Defendant made reasonable efforts to comply",
                    "Constitutional protections require proof beyond """
            """reasonable doubt"
                ],
                "case_citations": [
                    {
                        "case_name": "Miranda v. Arizona",
                        "year": 1966,
                        "citation": "384 U.S. 436",
                        "relevance": "Protects defendant's constitutional """
            """rights",
                        "excerpt": "Defendants have fundamental rights """
            """that must be protected"
                    }
                ],
                "statutes_cited": ["5th Amendment"],
                "confidence_score": 0.70,
                "weaknesses_acknowledged": ["Prosecution has """
            """circumstantial evidence"],
                "legal_reasoning": "The prosecution has failed to meet """
            """their burden of proof. The evidence is consistent with """
            """innocent conduct and good faith efforts at compliance."
            }""",
            # Moderator summary
            """Based on the arguments presented, both sides have made """
            """valid legal points. The prosecution has established a prima """
            """facie case, while the defense has raised reasonable doubt """
            """regarding intent. The key issue is whether the prosecution """
            """can prove willfulness beyond a reasonable doubt. Further """
            """evidence may be needed to resolve this question.""",
        ]

    def reset(self):
        """Reset the call count."""
        self.call_count = 0
