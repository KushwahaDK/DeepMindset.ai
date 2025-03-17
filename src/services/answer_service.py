"""
Answer service module

This module contains functionality for generating answers using OpenAI's GPT models.
"""
import logging
from openai import OpenAI
import streamlit as st

from src.config.app_config import get_openai_api_key

# Set up logging
logger = logging.getLogger(__name__)


def get_gpt_answer(question):
    """
    Get an answer from GPT model for the given question.
    
    Args:
        question (str): The question to ask GPT
        
    Returns:
        str: The answer from GPT
    """
    if not question:
        return "Please provide a question."
    
    try:
        client = OpenAI(api_key=get_openai_api_key())
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change the model as needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing concise answers to questions about any topic."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting answer from GPT: {str(e)}")
        return f"Error: {str(e)}" 