# question_generator.py
from openai import OpenAI
import json
import streamlit as st
from pydantic import BaseModel
from prompt import build_mcq_question_generation_prompt, build_subjective_question_generation_prompt

# Set your OpenAI API key via Streamlit secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

class MCQFormat(BaseModel):
    question: str
    options: list[str]
    correct_answers: list[int]
    explanation: str
    difficulty: str

class SubjectiveQuestionFormat(BaseModel):
    question: str
    explanation: str
    difficulty: str

def generate_mcq_question(topic, difficulty):

    prompt = build_mcq_question_generation_prompt(difficulty, topic)
    
    try:
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

        raw_output = response.choices[0].message.content.strip()

        return raw_output
    
    except Exception as e:
        return json.dumps({
            "question": "Error generating question.",
            "options": ["Error"],
            "correct_answers": [0],
            "explanation": str(e),
            "difficulty": difficulty
        })


def generate_subjective_question(topic, difficulty):
    prompt = build_subjective_question_generation_prompt(difficulty, topic)
    try:
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

        raw_output = response.choices[0].message.content.strip()

        return raw_output

    except Exception as e:
        return json.dumps({
            "question": "Error generating question.",
            "explanation": str(e),
            "difficulty": difficulty
        })


