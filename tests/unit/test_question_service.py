"""
Unit tests for the question service module.
"""
import unittest
import json
from unittest.mock import patch, MagicMock

from src.services.question_service import generate_mcq_question, generate_subjective_question
from src.utils.error_handlers import QuestionGenerationError


class TestQuestionService(unittest.TestCase):
    """Test cases for the question service module."""

    @patch("src.services.question_service.OpenAI")
    @patch("src.services.question_service.build_mcq_question_generation_prompt")
    def test_generate_mcq_question_success(self, mock_build_prompt, mock_openai):
        """Test generating an MCQ question successfully."""
        # Mock the prompt
        mock_build_prompt.return_value = "test prompt"
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock the response from OpenAI
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "question": "Test question?",
            "options": ["A", "B", "C", "D"],
            "correct_answers": [0],
            "explanation": "A is correct",
            "difficulty": "Easy"
        })
        mock_response.choices = [mock_choice]
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Call the function
        result = generate_mcq_question("Test Topic", "Easy")
        
        # Parse the result
        result_json = json.loads(result)
        
        # Verify the result
        self.assertEqual(result_json["question"], "Test question?")
        self.assertEqual(result_json["options"], ["A", "B", "C", "D"])
        self.assertEqual(result_json["correct_answers"], [0])
        self.assertEqual(result_json["explanation"], "A is correct")
        self.assertEqual(result_json["difficulty"], "Easy")
        
        # Verify that the OpenAI client was called correctly
        mock_client.beta.chat.completions.parse.assert_called_once()

    @patch("src.services.question_service.OpenAI")
    @patch("src.services.question_service.build_mcq_question_generation_prompt")
    def test_generate_mcq_question_error(self, mock_build_prompt, mock_openai):
        """Test handling an error when generating an MCQ question."""
        # Mock the prompt
        mock_build_prompt.return_value = "test prompt"
        
        # Mock the OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.chat.completions.parse.side_effect = Exception("Test error")
        
        # Call the function
        result = generate_mcq_question("Test Topic", "Easy")
        
        # Parse the result
        result_json = json.loads(result)
        
        # Verify the result contains an error message
        self.assertEqual(result_json["question"], "Error generating question.")
        self.assertEqual(result_json["options"], ["Error"])
        self.assertEqual(result_json["correct_answers"], [0])
        self.assertEqual(result_json["explanation"], "Test error")
        self.assertEqual(result_json["difficulty"], "Easy")

    @patch("src.services.question_service.OpenAI")
    @patch("src.services.question_service.build_subjective_question_generation_prompt")
    def test_generate_subjective_question_success(self, mock_build_prompt, mock_openai):
        """Test generating a subjective question successfully."""
        # Mock the prompt
        mock_build_prompt.return_value = "test prompt"
        
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock the response from OpenAI
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps({
            "question": "Test subjective question?",
            "explanation": "Test explanation",
            "difficulty": "Easy"
        })
        mock_response.choices = [mock_choice]
        mock_client.beta.chat.completions.parse.return_value = mock_response
        
        # Call the function
        result = generate_subjective_question("Test Topic", "Easy")
        
        # Parse the result
        result_json = json.loads(result)
        
        # Verify the result
        self.assertEqual(result_json["question"], "Test subjective question?")
        self.assertEqual(result_json["explanation"], "Test explanation")
        self.assertEqual(result_json["difficulty"], "Easy")
        
        # Verify that the OpenAI client was called correctly
        mock_client.beta.chat.completions.parse.assert_called_once()

    @patch("src.services.question_service.OpenAI")
    @patch("src.services.question_service.build_subjective_question_generation_prompt")
    def test_generate_subjective_question_error(self, mock_build_prompt, mock_openai):
        """Test handling an error when generating a subjective question."""
        # Mock the prompt
        mock_build_prompt.return_value = "test prompt"
        
        # Mock the OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.beta.chat.completions.parse.side_effect = Exception("Test error")
        
        # Call the function
        result = generate_subjective_question("Test Topic", "Easy")
        
        # Parse the result
        result_json = json.loads(result)
        
        # Verify the result contains an error message
        self.assertEqual(result_json["question"], "Error generating question.")
        self.assertEqual(result_json["explanation"], "Test error")
        self.assertEqual(result_json["difficulty"], "Easy")


if __name__ == "__main__":
    unittest.main() 