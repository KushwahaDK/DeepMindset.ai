"""
DeepMindset.ai - Main application entry point

This is the main entry point for the DeepMindset.ai application,
a Streamlit-based chat quiz application that leverages RAG.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app from the src module
from src.app import main

if __name__ == "__main__":
    main() 