import random
import glob
import json


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

def get_random_topic():
    """
    Loads a random path of subtopics from JSON files in the topic_store/topics directory.

    Returns:
        str: A comma-separated string representing the path of selected topics if found, otherwise None.
    """
    topic_files = glob.glob('topic_store/topics/*.json')  # Get all JSON files in the specified directory
    if not topic_files:
        print("No topic files found.")
        return None
    
    selected_file = random.choice(topic_files)  # Select a random file
    with open(selected_file, 'r') as f:
        topic_data = json.load(f)  # Load the JSON content
        
        # Randomly decide whether to start from the main topic or a subtopic
        if 'subTopics' in topic_data and isinstance(topic_data['subTopics'], list) and topic_data['subTopics']:
            if random.choice([True, False]):  # Randomly choose to start from a subtopic
                selected_subtopic = random.choice(topic_data['subTopics'])
                return ', '.join(load_random_subtopic(selected_subtopic))  # Start from a random subtopic
        
        # If not starting from a subtopic, start from the main topic
        return ', '.join(load_random_subtopic(topic_data))  # Return as a comma-separated string

if __name__ == "__main__":
    topic_path = get_random_topic()
    print(topic_path)


