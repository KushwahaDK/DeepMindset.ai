"""
Question models module

This module contains Pydantic models for question data.
"""
from pydantic import BaseModel, Field
from typing import List


class MCQFormat(BaseModel):
    """
    Model for multiple-choice questions.
    """
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of options")
    correct_answers: List[int] = Field(..., description="List of indices of correct options")
    explanation: str = Field(..., description="Explanation of the correct answer")
    difficulty: str = Field(..., description="Difficulty level of the question")


class SubjectiveQuestionFormat(BaseModel):
    """
    Model for subjective questions.
    """
    question: str = Field(..., description="The question text")
    explanation: str = Field(..., description="Explanation or answer to the question")
    difficulty: str = Field(..., description="Difficulty level of the question") 