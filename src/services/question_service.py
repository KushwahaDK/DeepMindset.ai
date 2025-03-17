"""
Question service module

This module provides functionality for generating quiz questions using OpenAI API.
"""
import json
import logging
from openai import OpenAI

from src.config.app_config import get_openai_api_key
from src.services.prompt_service import (
    build_mcq_question_generation_prompt,
    build_subjective_question_generation_prompt,
    build_coding_question_generation_prompt
)
from src.models.question_models import MCQFormat, SubjectiveQuestionFormat, CodingQuestionFormat
from src.utils.error_handlers import handle_exceptions, QuestionGenerationError

# Set up logging
logger = logging.getLogger(__name__)


@handle_exceptions
def generate_mcq_question(topic, difficulty):
    """
    Generate a multiple-choice question for the given topic and difficulty.
    
    Args:
        topic (str): The topic or topic path for the question
        difficulty (str): The difficulty level for the question
        
    Returns:
        str: JSON string representing the generated question
        
    Raises:
        QuestionGenerationError: If there's an error generating the question
    """
    logger.info(f"Generating MCQ for topic: {topic}, difficulty: {difficulty}")
    
    # Build the prompt for GPT
    prompt = build_mcq_question_generation_prompt(difficulty, topic)
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=get_openai_api_key())
        
        # Call the OpenAI API
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert educator and question generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format=MCQFormat,
            max_completion_tokens=800
        )
        
        # Extract and return the response content
        raw_output = response.choices[0].message.content.strip()
        logger.debug(f"Generated MCQ: {raw_output[:100]}...")  # Log first 100 chars of response
        
        return raw_output
    
    except Exception as e:
        logger.error(f"Error generating MCQ: {str(e)}")
        # Return a formatted error message as JSON
        error_response = {
            "question": "Error generating question.",
            "options": ["Error"],
            "correct_answers": [0],
            "explanation": str(e),
            "difficulty": difficulty
        }
        return json.dumps(error_response)


@handle_exceptions
def generate_subjective_question(topic, difficulty):
    """
    Generate a subjective question for the given topic and difficulty.
    
    Args:
        topic (str): The topic or topic path for the question
        difficulty (str): The difficulty level for the question
        
    Returns:
        str: JSON string representing the generated question
        
    Raises:
        QuestionGenerationError: If there's an error generating the question
    """
    logger.info(f"Generating subjective question for topic: {topic}, difficulty: {difficulty}")
    
    # Build the prompt for GPT
    prompt = build_subjective_question_generation_prompt(difficulty, topic)
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=get_openai_api_key())
        
        # Call the OpenAI API
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert educator and question generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format=SubjectiveQuestionFormat,
            max_completion_tokens=800
        )
        
        # Extract and return the response content
        raw_output = response.choices[0].message.content.strip()
        logger.debug(f"Generated subjective question: {raw_output[:100]}...")  # Log first 100 chars of response
        
        return raw_output
    
    except Exception as e:
        logger.error(f"Error generating subjective question: {str(e)}")
        # Return a formatted error message as JSON
        error_response = {
            "question": "Error generating question.",
            "explanation": str(e),
            "difficulty": difficulty
        }
        return json.dumps(error_response)


@handle_exceptions
def generate_coding_question(topic, difficulty):
    """
    Generate a coding interview question based on difficulty, without topic constraint.
    
    Args:
        topic (str or None): The topic or topic path (optional, not used for generation)
        difficulty (str): The difficulty level for the question
        
    Returns:
        str: JSON string representing the generated question
        
    Raises:
        QuestionGenerationError: If there's an error generating the question
    """
    logger.info(f"Generating coding interview question with difficulty: {difficulty}")
    
    # Build the prompt for GPT, passing None for topic since we don't want to use it
    prompt = build_coding_question_generation_prompt(difficulty, None)
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=get_openai_api_key())
        
        # Call the OpenAI API
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert programmer and technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format=CodingQuestionFormat,
            max_completion_tokens=1500
        )
        
        # Extract and return the response content
        raw_output = response.choices[0].message.content.strip()
        logger.debug(f"Generated coding question: {raw_output[:100]}...")  # Log first 100 chars of response
        
        return raw_output
    
    except Exception as e:
        logger.error(f"Error generating coding question: {str(e)}")
        # Return a formatted error message as JSON
        error_response = {
            "question": "Error generating question.",
            "description": "Unable to generate a coding interview question at this time.",
            "solution": "N/A",
            "explanation": str(e),
            "difficulty": difficulty
        }
        return json.dumps(error_response) 