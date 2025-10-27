"""
Legal Debate System - Streamlit Web Application
Multi-agent legal debate system using LangChain, LangGraph, and Google Gemini

This is a thin shim that preserves the original entrypoint.
The actual application logic is in src.app.main
"""

# Import and run the main app from the refactored module
from src.app.main import main

if __name__ == "__main__":
    main()
