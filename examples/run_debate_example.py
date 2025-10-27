#!/usr/bin/env python3
"""
Example script demonstrating the Legal Debate System in deterministic mode.

This script shows how to use the core orchestrator without any API keys,
using the built-in MockLLM for predictable, deterministic responses.

Run this script from the repository root:
    python examples/run_debate_example.py
"""

import sys
import os

# Add parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.orchestrator import DebateOrchestrator
from src.core.messages import AgentRole
from src.utils.llm_client import LLMClient


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Run a complete debate example."""
    print_section("Legal Debate System - Deterministic Mode Example")

    # Create LLM client (will use MockLLM since no API key is provided)
    print("🤖 Initializing MockLLM (no API key required)...")
    llm_client = LLMClient()
    status = llm_client.get_status()
    print(f"   Mode: {status['mode']}")
    print(f"   Model: {status['model']}")
    print(f"   Has API Key: {status['has_api_key']}")

    # Create orchestrator
    print("\n⚖️  Creating debate orchestrator...")
    orchestrator = DebateOrchestrator(llm_client=llm_client, max_rounds=2)
    print(f"   Max rounds: {orchestrator.max_rounds}")

    # Define the legal case
    case = """Case: State v. Johnson

The defendant, Sarah Johnson, was arrested after police officers conducted a 
warrantless search of her vehicle during a routine traffic stop. Officers 
discovered illegal substances in the trunk.

Legal Issues:
1. Was the warrantless search constitutional under the Fourth Amendment?
2. Did officers have probable cause or reasonable suspicion?
3. Should evidence be excluded under the exclusionary rule?

The prosecution argues the search was justified under the automobile exception 
and plain view doctrine. The defense contends this was an illegal search 
violating constitutional rights and that all evidence should be suppressed.
"""

    # Start the debate
    print_section("Starting Debate")
    print(f"Topic:\n{case}")

    orchestrator.start_debate(case)

    # Run debate rounds
    for round_num in range(1, orchestrator.max_rounds + 1):
        print_section(f"Round {round_num} of {orchestrator.max_rounds}")

        messages = orchestrator.step()

        # Display prosecution argument
        prosecution_msg = [m for m in messages if m.role == AgentRole.PROSECUTION][0]
        print("🔴 PROSECUTION:")
        print(f"   {prosecution_msg.content}\n")

        # Display defense argument
        defense_msg = [m for m in messages if m.role == AgentRole.DEFENSE][0]
        print("🔵 DEFENSE:")
        print(f"   {defense_msg.content}\n")

    # Get judge's evaluation
    print_section("Judge's Evaluation")
    result = orchestrator.evaluate()

    print("👨‍⚖️ JUDGE'S DECISION:")
    print(f"   {result.judge_reasoning}\n")

    # Display scores and winner
    print_section("Final Results")
    print(f"Prosecution Score: {result.scores['prosecution']}/10")
    print(f"Defense Score:     {result.scores['defense']}/10")

    if result.winner:
        print(f"\n🏆 Winner: {result.winner.value.upper()}")
    else:
        print("\n🤝 Result: TIE")

    # Display statistics
    print_section("Debate Statistics")
    print(f"Total Messages:     {len(result.messages)}")
    print(f"Rounds Completed:   {orchestrator.max_rounds}")
    print(
        f"Prosecution Args:   {len(result.get_messages_by_role(AgentRole.PROSECUTION))}"
    )
    print(f"Defense Args:       {len(result.get_messages_by_role(AgentRole.DEFENSE))}")
    print(f"Judge Evaluations:  {len(result.get_messages_by_role(AgentRole.JUDGE))}")

    print("\n" + "=" * 70)
    print("  Debate Complete!")
    print("=" * 70 + "\n")

    print("💡 Note: This example uses deterministic MockLLM responses.")
    print("   To use real LLM, set OPENAI_API_KEY environment variable.\n")


if __name__ == "__main__":
    main()
