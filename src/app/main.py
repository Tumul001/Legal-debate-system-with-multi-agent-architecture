"""
Legal Debate System - Streamlit Web Application
Multi-agent legal debate system with simplified orchestration
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.core.orchestrator import DebateOrchestrator
from src.core.messages import AgentRole
from src.utils.llm_client import LLMClient

# Load environment variables
load_dotenv()


def run_streamlit_app():
    """Main function to run the Streamlit app."""

    # Set page configuration
    st.set_page_config(
        page_title="Legal Debate System",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for better styling
    st.markdown(
        """
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.2rem;
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
        }
        .debate-section {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .prosecution {
            border-left: 5px solid #ff4b4b;
        }
        .defense {
            border-left: 5px solid #4b7bff;
        }
        .judge {
            border-left: 5px solid #ffa500;
        }
        .final-judgement {
            border-left: 5px solid #28a745;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        '<div class="main-header">⚖️ Legal Debate System</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">AI-Powered Multi-Agent Legal Debate</div>',
        unsafe_allow_html=True,
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key input (optional - will use MockLLM if not provided)
        api_key = st.text_input(
            "OpenAI API Key (optional)",
            type="password",
            help="Leave blank to use deterministic mock LLM for testing",
        )

        # Check if we're in mock mode
        use_mock = not api_key or os.getenv("MOCK_LLM", "false").lower() == "true"

        if use_mock:
            st.info("🤖 Using Mock LLM (Deterministic Mode)")
        else:
            st.success("🌐 Using Real LLM")

        st.divider()

        # Debate settings
        st.subheader("Debate Settings")
        max_rounds = st.slider("Maximum Rounds", min_value=1, max_value=5, value=3)

        st.divider()

        st.markdown(
            """
        ### About
        This system uses multiple AI agents to conduct structured legal debates:
        - **Prosecution**: Builds case for conviction
        - **Defense**: Defends the accused
        - **Judge**: Evaluates and scores arguments
        
        In deterministic mode (no API key), responses are predictable for testing.
        """
        )

    # Main content area
    st.header("📋 Enter Case Details")

    # Case description input
    default_case = """Case: State v. Smith
    
The defendant, John Smith, was arrested after police officers observed him making what they believed to be a drug transaction in a public park. Officers approached without a warrant and searched his backpack, finding illegal substances.

Legal Issues:
1. Was the warrantless search constitutional under the Fourth Amendment?
2. Did officers have probable cause or reasonable suspicion?
3. Should evidence be excluded under the exclusionary rule?

The prosecution argues the search was justified under the plain view doctrine and exigent circumstances. The defense contends this was an illegal search violating constitutional rights."""

    case_description = st.text_area(
        "Case Description",
        value=default_case,
        height=250,
        help="Enter the legal case details and issues to be debated",
    )

    # Start debate button
    if st.button("🎯 Start Legal Debate", type="primary"):
        if not case_description.strip():
            st.error("Please enter a case description")
            return

        # Create orchestrator with appropriate LLM client
        llm_client = LLMClient(api_key=api_key) if api_key else LLMClient()
        orchestrator = DebateOrchestrator(llm_client=llm_client, max_rounds=max_rounds)

        # Start the debate
        with st.spinner("Initializing debate..."):
            orchestrator.start_debate(case_description)

        st.success(f"Debate initialized! Running {max_rounds} rounds...")

        # Run debate rounds
        for round_num in range(1, max_rounds + 1):
            st.subheader(f"📍 Round {round_num} of {max_rounds}")

            with st.spinner(f"Round {round_num} in progress..."):
                messages = orchestrator.step()

            if not messages:
                break

            # Display prosecution argument
            prosecution_msg = [m for m in messages if m.role == AgentRole.PROSECUTION][
                0
            ]
            with st.container():
                st.markdown(
                    '<div class="debate-section prosecution">', unsafe_allow_html=True
                )
                st.markdown("#### 🔴 Prosecution Argument")
                st.write(prosecution_msg.content)
                st.markdown("</div>", unsafe_allow_html=True)

            # Display defense argument
            defense_msg = [m for m in messages if m.role == AgentRole.DEFENSE][0]
            with st.container():
                st.markdown(
                    '<div class="debate-section defense">', unsafe_allow_html=True
                )
                st.markdown("#### 🔵 Defense Argument")
                st.write(defense_msg.content)
                st.markdown("</div>", unsafe_allow_html=True)

        # Get final evaluation
        st.subheader("⚖️ Final Judgement")

        with st.spinner("Judge is deliberating..."):
            result = orchestrator.evaluate()

        # Display judge's decision
        with st.container():
            st.markdown(
                '<div class="debate-section final-judgement">', unsafe_allow_html=True
            )
            st.markdown("#### 👨‍⚖️ Judge's Decision")
            st.write(result.judge_reasoning)

            # Display scores
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Prosecution Score", f"{result.scores.get('prosecution', 0)}/10"
                )
            with col2:
                st.metric("Defense Score", f"{result.scores.get('defense', 0)}/10")
            with col3:
                if result.winner:
                    winner_name = result.winner.value.capitalize()
                    st.metric("Winner", winner_name)
                else:
                    st.metric("Result", "Tie")

            st.markdown("</div>", unsafe_allow_html=True)

        # Show debate statistics
        with st.expander("📊 Debate Statistics"):
            st.write(f"**Total Messages:** {len(result.messages)}")
            st.write(f"**Rounds Completed:** {max_rounds}")
            st.write(
                f"**Mode:** {'Mock LLM (Deterministic)' if use_mock else 'Real LLM'}"
            )

            # Message breakdown
            prosecution_count = len(result.get_messages_by_role(AgentRole.PROSECUTION))
            defense_count = len(result.get_messages_by_role(AgentRole.DEFENSE))
            judge_count = len(result.get_messages_by_role(AgentRole.JUDGE))

            st.write(f"**Messages by Role:**")
            st.write(f"  - Prosecution: {prosecution_count}")
            st.write(f"  - Defense: {defense_count}")
            st.write(f"  - Judge: {judge_count}")


if __name__ == "__main__":
    run_streamlit_app()
