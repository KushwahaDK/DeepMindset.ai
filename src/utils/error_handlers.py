"""
Error handling utilities module

This module contains utility functions for handling errors in the application.
"""
import logging
import traceback
import functools

# Set up logging
logger = logging.getLogger(__name__)


class QuestionGenerationError(Exception):
    """Exception raised for errors during question generation."""
    pass


class TopicRetrievalError(Exception):
    """Exception raised for errors during topic retrieval."""
    pass


def handle_exceptions(func):
    """
    Decorator to handle exceptions in functions.
    
    Args:
        func: The function to wrap
        
    Returns:
        The wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    return wrapper


def safe_json_parse(json_string, default=None):
    """
    Safely parse a JSON string.
    
    Args:
        json_string: The JSON string to parse
        default: The default value to return if parsing fails
        
    Returns:
        The parsed JSON data or the default value
    """
    import json
    
    if not json_string:
        return default
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return default 