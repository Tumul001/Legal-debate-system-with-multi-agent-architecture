"""
Legal Debate System - Streamlit Web Application Entry Point

This is a thin shim that imports and runs the main Streamlit application
from the src.app.main module.
"""

# Import the main application runner
from src.app.main import run_streamlit_app

# Run the Streamlit application
if __name__ == "__main__":
    run_streamlit_app()
else:
    # When imported, also run the app (for streamlit run app.py)
    run_streamlit_app()
