"""
Unit tests for the topic service module.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from src.services.topic_service import (
    parse_indented_file,
    generate_json_from_indented_file,
    update_topics,
    load_random_subtopic,
    get_random_topic
)
from src.utils.error_handlers import TopicRetrievalError


class TestTopicService(unittest.TestCase):
    """Test cases for the topic service module."""

    def test_parse_indented_file(self):
        """Test parsing an indented file."""
        mock_file_content = """Topic 1
    Subtopic 1.1
        Subtopic 1.1.1
    Subtopic 1.2
Topic 2
    Subtopic 2.1
"""
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = parse_indented_file("fake_path.txt")
            self.assertEqual(result["topicName"], "Topic 1")
            self.assertEqual(len(result["subTopics"]), 2)  # Two subtopics
            self.assertEqual(result["subTopics"][0]["topicName"], "Subtopic 1.1")
            self.assertEqual(len(result["subTopics"][0]["subTopics"]), 1)  # One sub-subtopic

    def test_generate_json_from_indented_file(self):
        """Test generating JSON from an indented file."""
        mock_file_content = """Topic 1
    Subtopic 1.1
"""
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("builtins.open", mock_open(read_data=mock_file_content)):
                with patch("json.dump") as mock_json_dump:
                    result = generate_json_from_indented_file("fake_path.txt", tmp_dir)
                    self.assertTrue(result)
                    mock_json_dump.assert_called_once()

    @patch("src.services.topic_service.glob.glob")
    @patch("src.services.topic_service.generate_json_from_indented_file")
    def test_update_topics_success(self, mock_generate, mock_glob):
        """Test updating topics successfully."""
        mock_glob.return_value = ["file1.txt", "file2.txt"]
        mock_generate.return_value = True
        
        with patch("os.path.exists", return_value=True):
            result = update_topics()
            self.assertTrue(result)
            self.assertEqual(mock_generate.call_count, 2)  # Called for each file

    @patch("src.services.topic_service.glob.glob")
    def test_update_topics_no_files(self, mock_glob):
        """Test updating topics with no files."""
        mock_glob.return_value = []
        
        with patch("os.path.exists", return_value=True):
            result = update_topics()
            self.assertFalse(result)

    def test_load_random_subtopic(self):
        """Test loading a random subtopic."""
        # Create a mock topic with subtopics
        mock_topic = {
            "topicName": "Topic 1",
            "subTopics": [
                {
                    "topicName": "Subtopic 1.1",
                    "subTopics": []
                }
            ]
        }
        
        with patch("random.choice", return_value=mock_topic["subTopics"][0]):
            result = load_random_subtopic(mock_topic)
            self.assertEqual(len(result), 2)  # Topic and subtopic
            self.assertEqual(result[0], "Topic 1")
            self.assertEqual(result[1], "Subtopic 1.1")

    @patch("src.services.topic_service.glob.glob")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("random.choice")
    def test_get_random_topic(self, mock_random, mock_json_load, mock_file_open, mock_glob):
        """Test getting a random topic."""
        # Mock the glob to return a file
        mock_glob.return_value = ["topic1.json"]
        
        # Mock the random choice to return the first file
        mock_random.side_effect = lambda x: x[0]
        
        # Mock the JSON load to return a topic
        mock_topic = {
            "topicName": "Topic 1",
            "subTopics": []
        }
        mock_json_load.return_value = mock_topic
        
        result = get_random_topic()
        self.assertEqual(result, "Topic 1")

    @patch("src.services.topic_service.glob.glob")
    def test_get_random_topic_no_files(self, mock_glob):
        """Test getting a random topic with no files."""
        mock_glob.return_value = []
        
        with self.assertRaises(TopicRetrievalError):
            get_random_topic()


if __name__ == "__main__":
    unittest.main() 