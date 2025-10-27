"""
Legal Debate System - Streamlit Web Application
Multi-agent legal debate system using LangChain, LangGraph, and Google Gemini

NOTE: This file is maintained for backward compatibility as the original entrypoint.
The refactored modular code is available in:
- src/app/main.py (Streamlit UI)
- src/core/ (Business logic: orchestrator, messages)
- src/utils/ (Utilities: LLM client, MockLLM)

You can run either:
- streamlit run app.py (this file - original monolithic version)
- streamlit run src/app/main.py (refactored modular version)
"""

import streamlit as st
import os
from typing import List
from dotenv import load_dotenv
from textblob import TextBlob

# Import all necessary components
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage
from langchain_community.vectorstores import FAISS
from langgraph.graph import StateGraph, END
from typing import TypedDict
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Legal Debate System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
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
    .moderator {
        border-left: 5px solid #ffa500;
    }
    .final-judgement {
        border-left: 5px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# =======================
# Schema Definitions
# =======================

class LegalCitation(BaseModel):
    """Represents a single case law citation"""
    case_name: str = Field(description="Name of the legal case")
    year: int = Field(description="Year of the decision")
    citation: str = Field(description="Official citation")
    relevance: str = Field(description="How this case applies to current argument")
    excerpt: str = Field(description="Key legal principle from the case")

class LegalArgument(BaseModel):
    """Structured output for a legal agent's argument"""
    position: str = Field(description="Either 'prosecution' or 'defense'")
    main_argument: str = Field(description="Core legal argument in 2-3 sentences")
    supporting_points: List[str] = Field(description="3-5 supporting arguments")
    case_citations: List[LegalCitation] = Field(description="Relevant case law citations")
    statutes_cited: List[str] = Field(description="Relevant statutes or legal codes")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in argument strength")
    weaknesses_acknowledged: List[str] = Field(description="Potential counterarguments")
    legal_reasoning: str = Field(description="Detailed reasoning connecting facts to law")

class DebateState(TypedDict):
    """The state object that gets passed between agents"""
    case_description: str
    prosecution_arguments: List[LegalArgument]
    defense_arguments: List[LegalArgument]
    debate_round: int
    moderator_summary: str
    final_judgement: str
    case_citations_pool: List[LegalCitation]

# =======================
# ML-Based Confidence Scoring
# =======================

def calculate_ml_confidence_score(argument: LegalArgument, state: DebateState = None) -> float:
    """
    Calculate confidence score using ML-based sentiment analysis and multiple factors
    
    Args:
        argument: The legal argument to score
        state: Optional debate state for context-aware scoring
    
    Returns:
        Confidence score between 0.0 and 1.0
    """
    
    # Factor 1: Sentiment Analysis (40% weight)
    # Analyze the positivity/assertiveness of the main argument
    blob = TextBlob(argument.main_argument)
    sentiment_polarity = blob.sentiment.polarity  # Range: -1 to 1
    sentiment_subjectivity = blob.sentiment.subjectivity  # Range: 0 to 1
    
    # Convert polarity to confidence (more positive = more confident)
    # Legal arguments should be assertive (positive) but not overly subjective
    sentiment_score = (sentiment_polarity + 1) / 2  # Normalize to 0-1
    objectivity_bonus = (1 - sentiment_subjectivity) * 0.2  # Less subjective is better
    sentiment_confidence = min((sentiment_score + objectivity_bonus), 1.0) * 0.4
    
    # Factor 2: Citation Quality (30% weight)
    # More citations and recent cases = higher confidence
    citation_count = len(argument.case_citations)
    citation_score = min(citation_count / 5.0, 1.0)  # Optimal: 5 citations
    
    # Recent cases (1950-2025) score higher
    if citation_count > 0:
        recent_years = [c.year for c in argument.case_citations if 1950 <= c.year <= 2025]
        recency_bonus = len(recent_years) / citation_count * 0.1
    else:
        recency_bonus = 0.0
    
    citation_confidence = min((citation_score + recency_bonus), 1.0) * 0.3
    
    # Factor 3: Argument Thoroughness (20% weight)
    # Length and depth of reasoning indicates preparation
    reasoning_words = len(argument.legal_reasoning.split())
    supporting_points_count = len(argument.supporting_points)
    statute_count = len(argument.statutes_cited)
    
    thoroughness_score = (
        min(reasoning_words / 200.0, 1.0) * 0.5 +  # Target: 200 words
        min(supporting_points_count / 5.0, 1.0) * 0.3 +  # Target: 5 points
        min(statute_count / 3.0, 1.0) * 0.2  # Target: 3 statutes
    )
    thoroughness_confidence = thoroughness_score * 0.2
    
    # Factor 4: Acknowledged Weaknesses (10% weight)
    # Fewer weaknesses = higher confidence, but acknowledging some shows honesty
    weakness_count = len(argument.weaknesses_acknowledged)
    if weakness_count == 0:
        weakness_confidence = 0.05  # Too confident, suspicious
    elif weakness_count <= 2:
        weakness_confidence = 0.10  # Optimal: acknowledges 1-2 weaknesses
    else:
        weakness_confidence = max(0.10 - (weakness_count - 2) * 0.02, 0.0)  # Too many weaknesses
    
    # Combine all factors
    ml_confidence = (
        sentiment_confidence +
        citation_confidence +
        thoroughness_confidence +
        weakness_confidence
    )
    
    # Ensure score is between 0.0 and 1.0
    final_score = max(0.0, min(ml_confidence, 1.0))
    
    return round(final_score, 2)

def get_confidence_breakdown(argument: LegalArgument) -> dict:
    """
    Get detailed breakdown of confidence score components for debugging
    
    Returns:
        Dictionary with individual factor scores
    """
    blob = TextBlob(argument.main_argument)
    sentiment_polarity = blob.sentiment.polarity
    sentiment_subjectivity = blob.sentiment.subjectivity
    
    return {
        'sentiment_polarity': round(sentiment_polarity, 2),
        'sentiment_subjectivity': round(sentiment_subjectivity, 2),
        'citation_count': len(argument.case_citations),
        'statute_count': len(argument.statutes_cited),
        'reasoning_length': len(argument.legal_reasoning.split()),
        'supporting_points': len(argument.supporting_points),
        'weaknesses_count': len(argument.weaknesses_acknowledged)
    }

# =======================
# RAG System
# =======================

class LegalRAGSystem:
    """Retrieval-Augmented Generation system for case law"""
    
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = None
        
    def retrieve_relevant_cases(self, query: str, k: int = 5) -> List[str]:
        """Retrieve most relevant case law for a query"""
        # Mock data for demonstration
        return [
            "Miranda v. Arizona (1966): Suspects must be informed of rights before interrogation.",
            "Gideon v. Wainwright (1963): Right to legal counsel in criminal cases.",
            "Terry v. Ohio (1968): Police may conduct stop-and-frisk if reasonable suspicion exists."
        ]

# =======================
# Legal Agents
# =======================

class LegalDebateAgent:
    """Base class for legal debate agents"""
    
    def __init__(self, role: str, model_name: str = "gemini-2.0-flash-exp"):
        self.role = role
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
        self.rag_system = LegalRAGSystem()
        self.parser = PydanticOutputParser(pydantic_object=LegalArgument)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_instruction()),
            ("human", "{case_description}\n\n{retrieved_cases}\n\n{opponent_arguments}")
        ])
        
    def _get_system_instruction(self) -> str:
        """Returns the detailed instruction for this agent"""
        if self.role == "prosecution":
            return """
Role: You are an expert prosecution attorney in a structured legal debate system.

Instructions:
1. Analyze the case facts thoroughly
2. Review retrieved case law and identify supporting cases
3. Build your argument with:
   - Clear main_argument (2-3 sentences)
   - 3-5 supporting_points
   - Specific case_citations with relevance
   - Applicable statutes_cited
   - Detailed legal_reasoning
4. Anticipate counterarguments (weaknesses_acknowledged)
5. Assess confidence_score (0.0-1.0)
6. Output valid JSON matching LegalArgument schema

{format_instructions}

Be adversarial but fair. Present the strongest possible case for prosecution.
"""
        else:
            return """
Role: You are an expert defense attorney in a structured legal debate system.

Instructions:
1. Analyze the case and understand client's position
2. Review case law for rights protections and defense precedents
3. Build your defense with:
   - Clear main_argument defending client
   - supporting_points creating reasonable doubt
   - case_citations supporting defense
   - statutes_cited protecting defendant rights
   - legal_reasoning showing prosecution insufficiency
4. Counter prosecution arguments if provided
5. Acknowledge weaknesses_acknowledged
6. Provide confidence_score
7. Output valid JSON matching LegalArgument schema

{format_instructions}

Provide zealous defense within legal bounds.
"""
    
    def generate_argument(self, state: DebateState) -> LegalArgument:
        """Generate a legal argument based on current debate state"""
        retrieved_cases = self.rag_system.retrieve_relevant_cases(
            query=state["case_description"], k=5
        )
        
        opponent_args = ""
        if self.role == "defense" and state["prosecution_arguments"]:
            opponent_args = "Prosecution's Previous Arguments:\n" + "\n".join([
                f"- {arg.main_argument}" for arg in state["prosecution_arguments"]
            ])
        elif self.role == "prosecution" and state["defense_arguments"]:
            opponent_args = "Defense's Previous Arguments:\n" + "\n".join([
                f"- {arg.main_argument}" for arg in state["defense_arguments"]
            ])
        
        formatted_prompt = self.prompt.format_messages(
            case_description=state["case_description"],
            retrieved_cases="\n\n".join(retrieved_cases),
            opponent_arguments=opponent_args,
            format_instructions=self.parser.get_format_instructions()
        )
        
        response = self.llm.invoke(formatted_prompt)
        
        try:
            argument = self.parser.parse(response.content)
            
            # Replace LLM's confidence with ML-calculated confidence
            llm_confidence = argument.confidence_score
            ml_confidence = calculate_ml_confidence_score(argument, state)
            
            # Use weighted average: 60% ML, 40% LLM self-assessment
            final_confidence = (ml_confidence * 0.6) + (llm_confidence * 0.4)
            argument.confidence_score = round(final_confidence, 2)
            
            return argument
        except Exception as e:
            st.error(f"Parsing error: {e}")
            return self._retry_with_feedback(formatted_prompt, str(e))
    
    def _retry_with_feedback(self, original_prompt, error_msg):
        """Retry generation if parsing fails"""
        retry_prompt = original_prompt + [
            HumanMessage(content=f"Error: {error_msg}. Provide valid JSON response.")
        ]
        response = self.llm.invoke(retry_prompt)
        return self.parser.parse(response.content)

class ModeratorAgent:
    """Moderator evaluates arguments and guides consensus"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
Role: Impartial judge/moderator in legal debate system.

Responsibilities:
1. Evaluate argument strength (reasoning, citations, accuracy, consistency)
2. Identify key legal issues requiring resolution
3. Note strengths and weaknesses for each side
4. Guide toward fair consensus
5. Provide clear, structured analysis in plain English

Maintain objectivity based solely on legal merit.
"""),
            ("human", """
Case: {case_description}

Prosecution Arguments:
{prosecution_summary}

Defense Arguments:
{defense_summary}

Current Round: {debate_round}

Provide your moderator analysis.
""")
        ])
    
    def evaluate_debate(self, state: DebateState) -> str:
        """Evaluate current state of debate"""
        pros_summary = "\n\n".join([
            f"Argument {i+1}:\nMain Point: {arg.main_argument}\n"
            f"Key Citations: {', '.join([c.case_name for c in arg.case_citations[:2]])}\n"
            f"Confidence: {arg.confidence_score}"
            for i, arg in enumerate(state["prosecution_arguments"])
        ])
        
        def_summary = "\n\n".join([
            f"Argument {i+1}:\nMain Point: {arg.main_argument}\n"
            f"Key Citations: {', '.join([c.case_name for c in arg.case_citations[:2]])}\n"
            f"Confidence: {arg.confidence_score}"
            for i, arg in enumerate(state["defense_arguments"])
        ])
        
        formatted_prompt = self.prompt.format_messages(
            case_description=state["case_description"],
            prosecution_summary=pros_summary,
            defense_summary=def_summary,
            debate_round=state["debate_round"]
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content

# =======================
# LangGraph Workflow
# =======================

def create_legal_debate_graph(log_container=None):
    """Creates the multi-agent debate workflow using LangGraph"""
    
    prosecution_agent = LegalDebateAgent(role="prosecution")
    defense_agent = LegalDebateAgent(role="defense")
    moderator_agent = ModeratorAgent()
    
    workflow = StateGraph(DebateState)
    
    def log_message(message: str, icon: str = "📝"):
        """Log a message to the Streamlit container and console"""
        if log_container:
            log_container.markdown(f"{icon} {message}")
        print(f"{icon} {message}")
    
    def prosecution_node(state: DebateState) -> DebateState:
        """Prosecution agent generates its argument"""
        log_message(f"**Round {state['debate_round']}: Prosecution is preparing arguments...**", "🔴")
        with st.spinner("🔴 Prosecution is presenting arguments..."):
            argument = prosecution_agent.generate_argument(state)
            state["prosecution_arguments"].append(argument)
        log_message(f"Prosecution argument completed. Confidence: {argument.confidence_score:.2f}", "✅")
        return state
    
    def defense_node(state: DebateState) -> DebateState:
        """Defense agent generates its argument"""
        log_message(f"**Round {state['debate_round']}: Defense is preparing counter-arguments...**", "🔵")
        with st.spinner("🔵 Defense is presenting arguments..."):
            argument = defense_agent.generate_argument(state)
            state["defense_arguments"].append(argument)
        log_message(f"Defense argument completed. Confidence: {argument.confidence_score:.2f}", "✅")
        return state
    
    def moderator_node(state: DebateState) -> DebateState:
        """Moderator evaluates current debate state"""
        log_message(f"**Round {state['debate_round']}: Moderator is evaluating arguments...**", "⚖️")
        with st.spinner("⚖️ Moderator is evaluating arguments..."):
            summary = moderator_agent.evaluate_debate(state)
            state["moderator_summary"] = summary
        log_message(f"Moderator analysis completed for Round {state['debate_round']}", "✅")
        return state
    
    def should_continue(state: DebateState) -> str:
        """Decide if debate should continue or end"""
        if state["debate_round"] >= 3:
            log_message("**All rounds completed. Proceeding to final judgement...**", "🏁")
            return "end"
        log_message(f"Round {state['debate_round']} completed. Continuing to next round...", "🔄")
        return "continue"
    
    def increment_round(state: DebateState) -> DebateState:
        """Increment the debate round counter"""
        state["debate_round"] += 1
        log_message(f"**Starting Round {state['debate_round']}**", "📍")
        return state
    
    def final_judgement_node(state: DebateState) -> DebateState:
        """Generate final consensus judgement"""
        log_message("**Generating final judgement...**", "⚖️")
        with st.spinner("⚖️ Generating final judgement..."):
            judgement_prompt = f"""
Based on all arguments presented:

Prosecution Arguments: {len(state['prosecution_arguments'])} arguments
Defense Arguments: {len(state['defense_arguments'])} arguments

Moderator's Analysis: {state['moderator_summary']}

Provide a final legal judgement that:
1. States the decision clearly
2. Explains the legal reasoning
3. Cites the most important precedents
4. Acknowledges both sides' strongest points
5. Explains why one side prevailed (or if case is inconclusive)

Be thorough but concise (300-500 words).
"""
            response = moderator_agent.llm.invoke([HumanMessage(content=judgement_prompt)])
            state["final_judgement"] = response.content
        log_message("**Final judgement completed!**", "✅")
        return state
    
    workflow.add_node("prosecution", prosecution_node)
    workflow.add_node("defense", defense_node)
    workflow.add_node("moderator", moderator_node)
    workflow.add_node("increment_round", increment_round)
    workflow.add_node("final_judgement", final_judgement_node)
    
    workflow.set_entry_point("prosecution")
    workflow.add_edge("prosecution", "defense")
    workflow.add_edge("defense", "moderator")
    workflow.add_conditional_edges(
        "moderator",
        should_continue,
        {
            "continue": "increment_round",
            "end": "final_judgement"
        }
    )
    workflow.add_edge("increment_round", "prosecution")
    workflow.add_edge("final_judgement", END)
    
    return workflow.compile()

# =======================
# Streamlit UI
# =======================

def display_argument(argument: LegalArgument, role: str, round_num: int):
    """Display a legal argument in a formatted way"""
    css_class = "prosecution" if role == "prosecution" else "defense"
    icon = "🔴" if role == "prosecution" else "🔵"
    
    st.markdown(f'<div class="debate-section {css_class}">', unsafe_allow_html=True)
    st.markdown(f"### {icon} {role.upper()} - Round {round_num}")
    
    st.markdown(f"**Main Argument:**")
    st.write(argument.main_argument)
    
    # Display confidence score with ML breakdown
    st.markdown(f"**Confidence Score:** {argument.confidence_score:.2f} 🎯")
    
    # Show confidence breakdown in an expander
    breakdown = get_confidence_breakdown(argument)
    with st.expander("📊 ML Confidence Analysis"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sentiment Polarity", f"{breakdown['sentiment_polarity']:.2f}", 
                     help="Ranges from -1 (negative) to +1 (positive)")
            st.metric("Citation Count", breakdown['citation_count'], 
                     help="Number of case law citations")
            st.metric("Reasoning Length", f"{breakdown['reasoning_length']} words",
                     help="Length of legal reasoning")
        with col2:
            st.metric("Subjectivity", f"{breakdown['sentiment_subjectivity']:.2f}",
                     help="0 = objective, 1 = subjective")
            st.metric("Statute Count", breakdown['statute_count'],
                     help="Number of statutes cited")
            st.metric("Weaknesses", breakdown['weaknesses_count'],
                     help="Acknowledged counterarguments")
    
    with st.expander("📋 Supporting Points"):
        for i, point in enumerate(argument.supporting_points, 1):
            st.write(f"{i}. {point}")
    
    with st.expander("📚 Case Citations"):
        for citation in argument.case_citations:
            st.markdown(f"**{citation.case_name}** ({citation.year})")
            st.write(f"*Citation:* {citation.citation}")
            st.write(f"*Relevance:* {citation.relevance}")
            st.write(f"*Excerpt:* {citation.excerpt}")
            st.divider()
    
    with st.expander("📖 Statutes Cited"):
        for statute in argument.statutes_cited:
            st.write(f"• {statute}")
    
    with st.expander("⚠️ Acknowledged Weaknesses"):
        for weakness in argument.weaknesses_acknowledged:
            st.write(f"• {weakness}")
    
    with st.expander("🧠 Legal Reasoning"):
        st.write(argument.legal_reasoning)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Initialize session state for chat history
    if 'debate_history' not in st.session_state:
        st.session_state.debate_history = []
    
    # Header
    st.markdown('<p class="main-header">⚖️ Legal Debate System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Multi-Agent Legal Debate using Google Gemini</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📖 About")
        st.markdown("""
        This system uses multiple AI agents to conduct a legal debate:
        
        - **🔴 Prosecution Agent**: Builds case for prosecution
        - **🔵 Defense Agent**: Defends the accused
        - **⚖️ Moderator Agent**: Evaluates arguments impartially
        
        The debate runs for up to 3 rounds, with each agent presenting arguments based on case law and legal reasoning.
        """)
        
        st.divider()
        
        st.header("🔧 System Info")
        st.markdown(f"""
        - **Model**: gemini-2.0-flash-exp
        - **Max Rounds**: 3
        - **Framework**: LangChain + LangGraph
        """)
        
        st.divider()
        
        # Chat history in sidebar
        st.header("📜 Chat History")
        if st.session_state.debate_history:
            history_expander = st.expander(f"View {len(st.session_state.debate_history)} previous debate(s)", expanded=False)
            with history_expander:
                for idx, history_item in enumerate(reversed(st.session_state.debate_history), 1):
                    st.markdown(f"**Debate #{len(st.session_state.debate_history) - idx + 1}**")
                    st.caption(f"Case: {history_item['case'][:100]}...")
                    st.caption(f"Rounds: {history_item['rounds']} | Date: {history_item['timestamp']}")
                    if st.button(f"View Details", key=f"view_{idx}"):
                        st.session_state.selected_history = history_item
                    st.divider()
        else:
            st.info("No debate history yet. Run your first debate!")
    
    # Main content area
    st.header("📝 Enter Case Details")
    
    # Pre-filled example case
    default_case = """John Doe was arrested for theft after being stopped by police officers who noticed him acting suspiciously near a jewelry store. During the stop, officers found stolen jewelry in his backpack. However, John claims:
1. He was not informed of his Miranda rights before questioning
2. The search of his backpack was conducted without a warrant
3. The officers had no probable cause for the initial stop

Legal Question: Should the evidence (stolen jewelry) be admissible in court?"""
    
    case_description = st.text_area(
        "Case Description",
        value=default_case,
        height=200,
        help="Describe the legal case, including facts and legal questions"
    )
    
    # Run debate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_button = st.button("⚖️ Start Legal Debate", type="primary", use_container_width=True)
    
    # Run the debate
    if run_button:
        if not case_description.strip():
            st.error("❌ Please enter a case description")
            return
        
        st.divider()
        
        # Create logs container
        st.header("📋 Debate Logs")
        log_container = st.container()
        
        with log_container:
            st.markdown("### 🔄 Real-time Progress")
            log_area = st.empty()
            log_messages = []
            
            # Function to update logs
            def update_log(message):
                log_messages.append(message)
                log_area.markdown("\n\n".join(log_messages))
        
        st.divider()
        st.header("🎯 Debate Results")
        
        # Initialize state
        initial_state = {
            "case_description": case_description,
            "prosecution_arguments": [],
            "defense_arguments": [],
            "debate_round": 1,
            "moderator_summary": "",
            "final_judgement": "",
            "case_citations_pool": []
        }
        
        try:
            # Create and run the debate graph with log container
            from datetime import datetime
            
            # Override log_message to update Streamlit logs
            original_print = print
            
            def custom_log(message, icon="📝"):
                log_messages.append(f"{icon} {message}")
                log_area.markdown("\n\n".join(log_messages))
                original_print(f"{icon} {message}")
            
            app = create_legal_debate_graph(log_container=log_area)
            
            # Override the log function in the graph
            custom_log("🚀 **Debate System Initialized**", "🎯")
            custom_log(f"📝 Case Description: {case_description[:100]}...", "📄")
            custom_log("⚖️ **Starting Legal Debate - Round 1**", "🏁")
            
            with st.spinner("🔄 Running legal debate..."):
                final_state = app.invoke(initial_state)
            
            custom_log("✅ **Debate Completed Successfully!**", "🎉")
            st.success("✅ Debate completed successfully!")
            
            # Save to history
            history_entry = {
                'case': case_description,
                'rounds': final_state["debate_round"],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'prosecution_count': len(final_state["prosecution_arguments"]),
                'defense_count': len(final_state["defense_arguments"]),
                'final_state': final_state
            }
            st.session_state.debate_history.append(history_entry)
            
            # Display results
            st.divider()
            
            # Display arguments round by round
            max_rounds = max(len(final_state["prosecution_arguments"]), 
                           len(final_state["defense_arguments"]))
            
            for round_num in range(max_rounds):
                st.subheader(f"📍 Round {round_num + 1}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if round_num < len(final_state["prosecution_arguments"]):
                        display_argument(
                            final_state["prosecution_arguments"][round_num],
                            "prosecution",
                            round_num + 1
                        )
                
                with col2:
                    if round_num < len(final_state["defense_arguments"]):
                        display_argument(
                            final_state["defense_arguments"][round_num],
                            "defense",
                            round_num + 1
                        )
                
                st.divider()
            
            # Display moderator analysis
            if final_state["moderator_summary"]:
                st.markdown('<div class="debate-section moderator">', unsafe_allow_html=True)
                st.markdown("### ⚖️ MODERATOR ANALYSIS")
                st.write(final_state["moderator_summary"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Display final judgement
            if final_state["final_judgement"]:
                st.markdown('<div class="debate-section final-judgement">', unsafe_allow_html=True)
                st.markdown("### 🏛️ FINAL JUDGEMENT")
                st.write(final_state["final_judgement"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Summary statistics
            st.header("📊 Debate Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Rounds", final_state["debate_round"])
            
            with col2:
                st.metric("Prosecution Arguments", len(final_state["prosecution_arguments"]))
            
            with col3:
                st.metric("Defense Arguments", len(final_state["defense_arguments"]))
            
            # All citations used
            st.subheader("📚 All Case Citations Used")
            all_citations = []
            for arg in final_state['prosecution_arguments'] + final_state['defense_arguments']:
                for citation in arg.case_citations:
                    if citation.case_name not in [c.case_name for c in all_citations]:
                        all_citations.append(citation)
            
            for citation in all_citations:
                st.write(f"• **{citation.case_name}** ({citation.year}) - {citation.citation}")
        
        except Exception as e:
            st.error(f"❌ An error occurred during the debate: {str(e)}")
            st.exception(e)
    
    # Display previous debate history if available
    if st.session_state.debate_history and not run_button:
        st.divider()
        st.header("📚 Previous Debates")
        
        for idx, history_item in enumerate(reversed(st.session_state.debate_history[-3:]), 1):  # Show last 3
            with st.expander(f"Debate #{len(st.session_state.debate_history) - idx + 1} - {history_item['timestamp']}", expanded=False):
                st.markdown(f"**Case:** {history_item['case'][:200]}...")
                st.markdown(f"**Total Rounds:** {history_item['rounds']}")
                st.markdown(f"**Prosecution Arguments:** {history_item['prosecution_count']}")
                st.markdown(f"**Defense Arguments:** {history_item['defense_count']}")
                
                if st.button(f"View Full Debate", key=f"full_view_{idx}"):
                    st.session_state.view_full_debate = history_item['final_state']
                    st.rerun()

if __name__ == "__main__":
    main()
