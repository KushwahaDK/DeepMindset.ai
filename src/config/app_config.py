"""
Application configuration module

This module contains configuration-related functions for the application.
"""
import os
import streamlit as st


def setup_page_config():
    """
    Set up the Streamlit page configuration.
    
    This includes page title, favicon, layout, etc.
    """
    st.set_page_config(
        page_title="DeepMindset.ai",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def get_openai_api_key():
    """
    Get the OpenAI API key from Streamlit secrets or environment variable.
    
    Returns:
        str: The OpenAI API key
    """
    # Try to get from Streamlit secrets
    try:
        return st.secrets["openai"]["api_key"]
    except KeyError:
        # Fallback to environment variable
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not found. Please set it in .streamlit/secrets.toml or as an environment variable.")
        return api_key 