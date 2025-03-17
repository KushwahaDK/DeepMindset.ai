import json
import os
import glob

def parse_indented_file(file_path):
    """
    Parses an indented text file to create a nested topic structure.

    Args:
        file_path (str): The path to the indented text file.

    Returns:
        dict: A nested dictionary representing the topic structure.
    """
    with open(file_path, 'r') as f:
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



def generate_json_from_indented_file(input_file, output_directory):
    """
    Generates a JSON file from an indented text file.

    Args:
        input_file (str): The path to the indented text file.
        output_directory (str): The directory to save the generated JSON file.
    """
    topic_structure = parse_indented_file(input_file)

    if topic_structure:
        main_topic_name = topic_structure['topicName']
        output_file_path = os.path.join(output_directory, f"{main_topic_name.lower().replace(' ', '_')}.json")

        with open(output_file_path, 'w') as json_file:
            json.dump(topic_structure, json_file, indent=4)

        print(f"Generated JSON file: {output_file_path}")
    else:
        print("No topics found in the input file.")

# Example usage
def update_topics():
    output_dir = 'topic_store/topics/'  # Directory to save the JSON files
    raw_files = glob.glob('topic_store/raw/*.txt')  # Get all .txt files in the raw folder
    
    try:
        for input_file_path in raw_files:
            print(f"Processing: {input_file_path}")
            generate_json_from_indented_file(input_file_path, output_dir)
    
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
