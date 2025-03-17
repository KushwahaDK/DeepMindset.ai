"""
Prompt service module

This module provides prompt templates for GPT models to generate questions.
"""
import logging

# Set up logging
logger = logging.getLogger(__name__)


def build_mcq_question_generation_prompt(difficulty, topics):
    """
    Builds a prompt for GPT to generate MCQ-style questions.
    
    Args:
        difficulty (str): The difficulty level for the questions ("Easy", "Medium", "Hard", "Expert")
        topics (str): The hierarchy of topics/subtopics to cover
        
    Returns:
        str: The formatted prompt
    """
    return f"""
[SYSTEM / ROLE: Question Generator]

You are an expert question generator. You will produce subjective questions in a valid JSON format. Each generated question 
must reinforce understanding for specified hierarchy of topics & sub-topics with specified difficulty level. 
You are an expert technical interviewer for senior-level Machine Learning Engineering, AI Architecture, or Lead Data Science roles at a top-tier company. I will provide you with a single topic.
.You will produce multiple-choice questions (possibly multiple correct answers) in a valid JSON format. Each generated question 
must reinforce understanding for specified hierarchy of topics & sub-topics with specified difficulty level. 
Follow these rules:

1. **Format**: Provide the output as a JSON array. Each element in the array 
   should be an object with the following keys:
   - "question": (string) A clear and concise multiple-choice question.
   - "options": (list of strings) An array containing at least 4 possible options.
   - "correct_answers": (list of indices indicating the correct option(s), where index starts at 0). Provide one or more correct option(s) exactly as they appear 
     in "options". (If multiple correct answers exist, list them in an array.)
   - "explanation": (string) A detailed explanation about why the correct answer is correct or 
     relevant details for the user to learn from. If relevant to the question then provide a code example or math equation as well.
   - "difficulty": (string) Must exactly match one of the following: ["Easy", "Medium", "Hard", "Expert"] 
     (Use the difficulty specified below.)

2. **Content Requirements**:
   - Each question must reflect the specified difficulty level.
   - Incorporate the provided hoerarchy of topics & sub-topics in both the question wording 
     and the explanation.
   - Make sure the question is factually correct and self-contained, so it can be understood 
     without needing additional context.
   - If the question, options or explanations include formulas or math equations then enclose it with $ signs.

3. **General Approach**:
   - Focus on reinforcing the user's understanding by covering important aspects of 
     the subject matter.
   - Avoid extraneous content or irrelevant details.

4. **Answer Strictly in JSON**:
   - Do not include any markdown formatting or additional commentary outside the JSON array.
   - The JSON must be valid and parseable.

---
Now, generate multiple-choice questions based on the following user specifications:
- **Difficulty**: {difficulty}
- **Hierarchy of Topics & Sub-Topics**: {topics}

Use the guidelines above to produce the final JSON output.
"""


def build_subjective_question_generation_prompt(difficulty, topic):
    """
    Builds a prompt for GPT to generate subjective questions.
    
    Args:
        difficulty (str): The difficulty level for the questions ("Easy", "Medium", "Hard", "Expert")
        topic (str): The hierarchy of topics/subtopics to cover
        
    Returns:
        str: The formatted prompt
    """
    return f"""
[SYSTEM / ROLE: Question Generator]

You are an expert question generator. You will produce subjective questions in a valid JSON format. Each generated question 
must reinforce understanding for specified hierarchy of topics & sub-topics with specified difficulty level. 
You are an expert technical interviewer for senior-level Machine Learning Engineering, AI Architecture, or Lead Data Science roles at a top-tier company. I will provide you with a single topic.

Based on that topic, please craft:
- **One** {difficulty} interview question that probes deep understanding and requires a detailed, thoughtful response.
- The question should prompt the candidate to explain the underlying concepts, consider trade-offs, and discuss real-world implications or applications where possible.

1. **Format**: Provide the output as a JSON array. Each element in the array 
   should be an object with the following keys:
   - "question": (string) Question based on above craft guidelines
   - "explanation": (string) A detailed answer based on the question. If relevant to the question then provide a code example or math equation as well.
   - "difficulty": (string) Must exactly match one of the following: ["Easy", "Medium", "Hard", "Expert"] 
     (Use the difficulty specified below.)
Requirements:
1. The question must be sufficiently challenging and open-ended, requiring the candidate to demonstrate expertise and critical thinking.
2. It should test fundamental understanding of the topic, including any relevant complexities or nuances.
3. If the question or explanations include formulas or math equations then enclose it with $ signs.

Now, generate multiple-choice questions based on the following user specifications:
- **Difficulty**: {difficulty}
- **Hierarchy of Topics & Sub-Topics**: {topic}


Begin now.
""" 

def build_coding_question_generation_prompt(difficulty, topic=None):
    """
    Builds a prompt for GPT to generate coding interview questions based only on difficulty.
    
    Args:
        difficulty (str): The difficulty level for the questions ("Easy", "Medium", "Hard", "Expert")
        topic (str, optional): The hierarchy of topics/subtopics to cover (not used)
        
    Returns:
        str: The formatted prompt
    """
    # Creating a mapping of difficulty levels to types of questions to generate
    difficulty_focus = {
        "Easy": "Focus on fundamental programming concepts, basic data structures (arrays, strings, simple loops), and straightforward problem-solving.",
        "Medium": "Include questions on intermediate data structures (stacks, queues, trees), algorithms (sorting, searching, dynamic programming basics), and implementation of ML/DL components.",
        "Hard": "Cover advanced algorithms (complex dynamic programming, graph algorithms), optimizations, and implementations of ML/DL architectures like CNNs or RNNs.",
        "Expert": "Focus on cutting-edge ML/DL implementations (transformers, attention mechanisms, GANs), highly optimized algorithms, and complex system designs."
    }
    
    focus_instruction = difficulty_focus.get(difficulty, difficulty_focus["Medium"])
    
    return f"""
[SYSTEM / ROLE: Technical Interviewer and Programming Expert]

You are an expert technical interviewer specializing in coding interviews for Machine Learning, Deep Learning, and Software Engineering positions. You will generate a detailed coding interview question in JSON format based on the specified difficulty level.

For this {difficulty} level question:
{focus_instruction}

The question should:
- Be clear, concise, and focused on testing both theoretical understanding and practical implementation
- Include a well-defined problem statement with examples
- Provide a complete solution with explanation
- Match the specified difficulty level ({difficulty})

Please generate the question in the following JSON format:

1. **Format**: Provide the output as a JSON object with these keys:
   - "question": (string) A clear and concise title for the coding problem.
   - "description": (string) A detailed description of the problem, including context and requirements.
   - "examples": (string) Example inputs and expected outputs to clarify the requirements.
   - "constraints": (string) Any constraints or limitations for the problem.
   - "solution": (string) High-level explanation of the solution approach.
   - "code_solution": (string) A complete, well-commented code solution to the problem.
   - "starter_code": (string) A template with the basic structure for the user to start coding (e.g., function signature, class definition).
   - "language": (string) Programming language of the solution (default: "python").
   - "explanation": (string) Detailed explanation of how the code works, key concepts, and time/space complexity.
   - "difficulty": (string) Must exactly match one of: ["Easy", "Medium", "Hard", "Expert"] (use the specified difficulty).

2. **Difficulty Levels**:
   - Easy: Basic algorithms, simple implementations, 1-2 concepts.
   - Medium: Intermediate algorithms, data structures, optimization, combining 2-3 concepts.
   - Hard: Complex algorithms, optimizations, design patterns, combining multiple concepts.
   - Expert: Very advanced topics, cutting-edge ML/DL techniques, highly optimized solutions.

3. **Focus on Implementation**:
   - Include code that demonstrates the implementation, not just theoretical explanations.
   - For ML/DL questions, include relevant model architecture code or algorithm implementations.
   - For algorithm questions, provide efficient solutions with proper time/space complexity analysis.
   - The starter_code should provide just enough structure to get started, without giving away the solution.

4. **Answer Strictly in JSON**:
   - Do not include any markdown formatting or additional commentary outside the JSON.
   - The JSON must be valid and parseable.

---
Now, generate a coding interview question based on the following difficulty level:
- **Difficulty**: {difficulty}

The question should test practical coding skills at the appropriate level of complexity.
""" 