"""
Topic service module

This module provides functionality for managing and retrieving topics for the application.
"""
import json
import os
import glob
import random
import logging
from src.utils.error_handlers import handle_exceptions, TopicRetrievalError

# Set up logging
logger = logging.getLogger(__name__)


@handle_exceptions
def parse_indented_file(file_path):
    """
    Parses an indented text file to create a nested topic structure.

    Args:
        file_path (str): The path to the indented text file.

    Returns:
        dict: A nested dictionary representing the topic structure.
    """
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        topic_structure = None
        # Stack will store tuples of (topic, indentation_level)
        topic_stack = []

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:  # Skip empty lines
                continue

            # Compute indentation level (number of leading spaces)
            level = len(line) - len(line.lstrip())

            # Create a new topic
            new_topic = {
                'topicId': stripped_line.lower().replace(" ", "_"),
                'topicName': stripped_line,
                'subTopics': []
            }

            # Adjust the stack: pop until the top element has a lower indentation than the current level.
            while topic_stack and topic_stack[-1][1] >= level:
                topic_stack.pop()

            if not topic_stack:
                # This is the main (or a new root) topic
                topic_structure = new_topic
            else:
                # Add as a subtopic of the current parent
                topic_stack[-1][0]['subTopics'].append(new_topic)

            # Push the new topic and its level onto the stack
            topic_stack.append((new_topic, level))

        return topic_structure
    except Exception as e:
        logger.error(f"Error parsing indented file {file_path}: {str(e)}")
        raise


@handle_exceptions
def generate_json_from_indented_file(input_file, output_directory):
    """
    Generates a JSON file from an indented text file.

    Args:
        input_file (str): The path to the indented text file.
        output_directory (str): The directory to save the generated JSON file.
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    topic_structure = parse_indented_file(input_file)

    if topic_structure:
        main_topic_name = topic_structure['topicName']
        output_file_path = os.path.join(output_directory, f"{main_topic_name.lower().replace(' ', '_')}.json")

        with open(output_file_path, 'w', encoding="utf-8") as json_file:
            json.dump(topic_structure, json_file, indent=4)

        logger.info(f"Generated JSON file: {output_file_path}")
        return True
    else:
        logger.warning(f"No topics found in the input file: {input_file}")
        return False


@handle_exceptions
def update_topics():
    """
    Update topics by processing raw text files into JSON format.
    
    Returns:
        bool: True if successful, False otherwise
    """
    output_dir = 'topic_store/topics/'  # Directory to save the JSON files
    raw_dir = 'topic_store/raw/'  # Directory containing raw text files
    
    # Ensure directories exist
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    raw_files = glob.glob(os.path.join(raw_dir, '*.txt'))  # Get all .txt files in the raw folder
    
    if not raw_files:
        logger.warning("No raw topic files found to process.")
        return False
    
    success_count = 0
    for input_file_path in raw_files:
        try:
            logger.info(f"Processing: {input_file_path}")
            if generate_json_from_indented_file(input_file_path, output_dir):
                success_count += 1
        except Exception as e:
            logger.error(f"Error processing {input_file_path}: {str(e)}")
    
    return success_count > 0


@handle_exceptions
def load_random_subtopic(topic):
    """
    Recursively selects a random subtopic from a given topic.

    Args:
        topic (dict): The topic dictionary to extract a random subtopic from.

    Returns:
        list: A list representing the path of selected topics.
    """
    path = [topic['topicName']]  # Start with the current topic name

    if 'subTopics' in topic and isinstance(topic['subTopics'], list) and topic['subTopics']:
        # Select a random subtopic
        selected_subtopic = random.choice(topic['subTopics'])
        # Recursively get the path from the selected subtopic
        path.extend(load_random_subtopic(selected_subtopic))
    return path


@handle_exceptions
def get_random_topic():
    """
    Loads a random path of subtopics from JSON files in the topic_store/topics directory.

    Returns:
        str: A comma-separated string representing the path of selected topics if found, otherwise None.
    """
    topic_files = glob.glob('topic_store/topics/*.json')  # Get all JSON files in the specified directory
    if not topic_files:
        logger.warning("No topic files found.")
        raise TopicRetrievalError("No topic files found. Please update topics first.")
    
    selected_file = random.choice(topic_files)  # Select a random file
    try:
        with open(selected_file, 'r', encoding="utf-8") as f:
            topic_data = json.load(f)  # Load the JSON content
            
            # Randomly decide whether to start from the main topic or a subtopic
            if 'subTopics' in topic_data and isinstance(topic_data['subTopics'], list) and topic_data['subTopics']:
                if random.choice([True, False]):  # Randomly choose to start from a subtopic
                    selected_subtopic = random.choice(topic_data['subTopics'])
                    return ', '.join(load_random_subtopic(selected_subtopic))  # Start from a random subtopic
            
            # If not starting from a subtopic, start from the main topic
            return ', '.join(load_random_subtopic(topic_data))  # Return as a comma-separated string
    except Exception as e:
        logger.error(f"Error loading topic from {selected_file}: {str(e)}")
        raise TopicRetrievalError(f"Error loading topic: {str(e)}") 