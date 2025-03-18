"""
Main application module for DeepMindset.ai

This module contains the main application logic for the DeepMindset.ai application.
It handles the UI setup, navigation, and interaction with the various components.
"""
import streamlit as st
import json
import torch
import threading
import time
from code_editor import code_editor

from src.services.question_service import generate_mcq_question, generate_subjective_question, generate_coding_question
from src.services.topic_service import update_topics, get_random_topic
from src.services.answer_service import get_gpt_answer
from src.config.app_config import setup_page_config

# Fix for torch classes path issue
torch.classes.__path__ = []  # Manually set it to empty

# Initialize session state for minimal reruns
def initialize_session_state():
    """
    Initialize all session state variables at once to reduce reruns
    """
    if "initialized" not in st.session_state:
        # App state
        st.session_state.current_page = "MCQ"
        st.session_state.difficulty = "Medium"
        st.session_state.stay_topic = False
        
        # MCQ state
        st.session_state.mcq_question_data = None
        st.session_state.mcq_answered = False
        st.session_state.mcq_score = 0
        st.session_state.mcq_current_topic = None
        st.session_state.mcq_current_question_id = 0
        st.session_state.mcq_question_version = 0
        st.session_state.mcq_selected_options = []
        
        # Subjective state
        st.session_state.subj_question_data = None
        st.session_state.subj_answered = False
        st.session_state.subj_current_topic = None
        st.session_state.subj_current_question_id = 0
        st.session_state.subj_question_version = 0
        
        # Coding state
        st.session_state.coding_question_data = None
        st.session_state.coding_answered = False
        st.session_state.coding_current_topic = None
        st.session_state.coding_current_question_id = 0
        st.session_state.coding_question_version = 0
        st.session_state.user_code_input = ""
        
        # Search state
        st.session_state.search_history = []
        
        # Mark as initialized
        st.session_state.initialized = True
        


def main():
    """
    Main application function that sets up the Streamlit UI and handles user interactions.
    """
    # Set page configuration
    setup_page_config()
    
    # Initialize all session state at once
    initialize_session_state()

    # Create a layout with main content and right sidebar
    main_col, right_sidebar = st.columns([3, 1], gap="medium")

    with main_col:
        # Set up navigation in the sidebar
        setup_navigation()
        
        # Handle different pages based on user selection
        if st.session_state.current_page == "Update Topics":
            render_update_topics_page()
        elif st.session_state.current_page == "MCQ":
            render_mcq_page()
        elif st.session_state.current_page == "Subjectives":
            render_subjective_page()
        elif st.session_state.current_page == "Coding Interviews":
            render_coding_interview_page()

    # Right sidebar for quick search
    with right_sidebar:
        render_search_sidebar()


def setup_navigation():
    """
    Set up the navigation sidebar with buttons for different pages.
    """
    st.sidebar.title(":blue[DeepMindset.ai]")

    # Create navigation buttons
    if st.sidebar.button("MCQ", key="quiz_btn", use_container_width=True):
        st.session_state.current_page = "MCQ"
    if st.sidebar.button("Subjectives", key="subjectives_btn", use_container_width=True):
        st.session_state.current_page = "Subjectives"
    if st.sidebar.button("Coding Interviews", key="coding_btn", use_container_width=True):
        st.session_state.current_page = "Coding Interviews"
    if st.sidebar.button("Update Topics", key="update_topics_btn", use_container_width=True):
        st.session_state.current_page = "Update Topics"

    # Highlight the current page
    st.sidebar.markdown(f"**Current page:** {st.session_state.current_page}")

    # Add quiz settings to sidebar when on quiz pages
    if st.session_state.current_page in ["MCQ", "Subjectives", "Coding Interviews"]:
        st.sidebar.markdown("---")  # Add separator
        st.sidebar.markdown("### Quiz Settings")
        # Difficulty dropdown and stay on topic checkbox
        difficulty = st.sidebar.selectbox(
            "Select Difficulty", 
            ["Easy", "Medium", "Hard", "Expert"],
            index=1,
            key="difficulty_selector"
        )
        stay_topic = st.sidebar.checkbox(
            "Stay on same topic", 
            key="stay_topic_checkbox",
            value=False
        )
        
        # Only update session state when values actually change (reduces reruns)
        if difficulty != st.session_state.difficulty:
            st.session_state.difficulty = difficulty
            
        if stay_topic != st.session_state.stay_topic:
            st.session_state.stay_topic = stay_topic


def render_update_topics_page():
    """
    Render the Update Topics page.
    """
    st.header("Update Topics")
    
    st.write("This will scan the topic_store/raw directory for new topic files and generate JSON files in the topic_store/topics directory.")
    
    if st.button("Update Topics", key="update_topics_button"):
        with st.spinner("Updating topics..."):
            result = update_topics()
            if result:
                st.success("Topics updated successfully!")
            else:
                st.error("Failed to update topics. Please check the logs for more information.")


def render_mcq_page():
    """
    Render the MCQ quiz page with optimized performance.
    """
    # Load first question automatically if none exists
    if st.session_state.mcq_question_data is None:
        load_new_mcq_question()

    if st.session_state.mcq_question_data:
        question = st.session_state.mcq_question_data
        
        # Create a placeholder to manage dynamic content
        question_container = st.empty()

        with question_container.container():
            
            st.header(question["question"], divider="rainbow")
            st.write("###### Topics: " + st.session_state.mcq_current_topic)
            st.write("###### Difficulty Level: " + question["difficulty"])
            
            # Use radio buttons instead of checkboxes for single-selection MCQs
            # This reduces reruns for each selection
            if len(question["correct_answers"]) == 1:
                # Case: Single correct answer
                options = [(chr(97 + i) + ". " + option, i) for i, option in enumerate(question["options"])]
                selected_idx = st.radio(
                    "Select your answer:",
                    options,
                    format_func=lambda x: x[0],
                    key=f"radio_{st.session_state.mcq_current_question_id}_{st.session_state.mcq_question_version}"
                )
                
                # Update selected options based on radio selection
                st.session_state.mcq_selected_options = [question["options"][selected_idx[1]]]
            else:
                # Case: Multiple correct answers
                # Store checkbox states dynamically
                selected_options = []
                for i, option in enumerate(question["options"]):
                    key = f"option_{st.session_state.mcq_current_question_id}_{st.session_state.mcq_question_version}_{i}"
                    label = chr(97 + i) + ". " + option  # Convert index to letter (a, b, c, d)
                    is_checked = st.checkbox(label, key=key, value=option in st.session_state.mcq_selected_options)
                    if is_checked:
                        if option not in st.session_state.mcq_selected_options:
                            st.session_state.mcq_selected_options.append(option)
                    else:
                        if option in st.session_state.mcq_selected_options:
                            st.session_state.mcq_selected_options.remove(option)

            # Submit button logic
            if st.button("Submit", key="mcq_submit_button") and not st.session_state.mcq_answered:
                correct_options = [question["options"][i] for i in question["correct_answers"]]
                if set(st.session_state.mcq_selected_options) == set(correct_options):
                    st.success("Correct Answer!")
                    st.write("Correct Answers: " + ", ".join(correct_options))
                    st.session_state.mcq_score += 1
                else:
                    st.error("Wrong Answer!")
                    st.write("Correct Answers: " + ", ".join(correct_options))
                st.write("**Explanation:** " + question["explanation"])
                st.session_state.mcq_answered = True

            # Next button logic
            if st.session_state.mcq_answered:  # Show "Next" only after answering
                if st.button("Next Question", key="mcq_next_button", on_click=load_new_mcq_question):
                    pass

    st.write("### Your Score:", st.session_state.mcq_score)


def load_new_mcq_question():
    """
    Load a new MCQ question based on the current settings.
    """
    # Show a spinner while loading
    with st.spinner("Loading new question..."):
        if st.session_state.stay_topic:
            topic = st.session_state.mcq_current_topic
            if not topic:
                topic = get_random_topic()
                st.session_state.mcq_current_topic = topic
        else:
            topic = get_random_topic()
            st.session_state.mcq_current_topic = topic
        
        try:
            question_data = generate_mcq_question(topic, st.session_state.difficulty)
            st.session_state.mcq_question_data = json.loads(question_data)
            st.session_state.mcq_current_question_id += 1
            st.session_state.mcq_selected_options = []  # Reset selected options
            st.session_state.mcq_answered = False
            st.session_state.mcq_question_version += 1  # Increment version to refresh widgets
            
        except Exception as e:
            st.error(f"Failed to generate question: {str(e)}")
            st.session_state.mcq_question_data = None


def render_subjective_page():
    """
    Render the subjective questions page with optimized performance.
    """
    # Load first question automatically if none exists
    if st.session_state.subj_question_data is None:
        load_new_subjective_question()

    if st.session_state.subj_question_data:
        question = st.session_state.subj_question_data
        
        # Create a placeholder to manage dynamic content
        question_container = st.empty()

        with question_container.container():
            
            st.header(question["question"], divider="rainbow")
            st.write("###### Topics: " + st.session_state.subj_current_topic)
            st.write("###### Difficulty Level: " + question["difficulty"])
            
            # Submit button logic
            if st.button("Show Answer", key="subj_show_answer_button") and not st.session_state.subj_answered:
                st.write("**Explanation:** " + question["explanation"])
                st.session_state.subj_answered = True
                

            # Next button logic
            if st.button("Next Question", key="subj_next_button", on_click=load_new_subjective_question):
                pass


def load_new_subjective_question():
    """
    Load a new subjective question based on the current settings.
    """
    # Show a spinner while loading
    with st.spinner("Loading new question..."):
        if st.session_state.stay_topic:
            topic = st.session_state.subj_current_topic
            if not topic:
                topic = get_random_topic()
                st.session_state.subj_current_topic = topic
        else:
            topic = get_random_topic()
            st.session_state.subj_current_topic = topic
        
        try:
            question_data = generate_subjective_question(topic, st.session_state.difficulty)
            st.session_state.subj_question_data = json.loads(question_data)
            st.session_state.subj_current_question_id += 1
            st.session_state.subj_answered = False
            st.session_state.subj_question_version += 1  # Increment version to refresh widgets
            
        except Exception as e:
            st.error(f"Failed to generate question: {str(e)}")
            st.session_state.subj_question_data = None


def render_search_sidebar():
    """
    Render the quick search sidebar with optimized performance.
    """
    st.markdown("### Quick Search")
    st.write("Ask any question and get a quick answer.")
    
    # Search input and button
    search_query = st.text_area("Your question:", height=100)
    if st.button("Ask", key="ask_button"):
        if search_query:
            with st.spinner("Getting answer..."):
                answer = get_gpt_answer(search_query)
                # Add to search history
                st.session_state.search_history.append({"question": search_query, "answer": answer})
    
    # Display search history
    if st.session_state.search_history:
        st.markdown("### Recent Answers")
        for i, item in enumerate(reversed(st.session_state.search_history[-5:])):  # Show last 5 searches
            with st.expander(f"Q: {item['question'][:50]}..." if len(item['question']) > 50 else f"Q: {item['question']}"):
                st.markdown(f"**Answer:** {item['answer']}")


def render_coding_interview_page():
    """
    Render the coding interview questions page with optimized performance.
    """
    # Load first question automatically if none exists
    if st.session_state.coding_question_data is None:
        load_new_coding_question()

    if st.session_state.coding_question_data:
        question = st.session_state.coding_question_data
        
        # Create a placeholder to manage dynamic content
        question_container = st.empty()

        with question_container.container():
            st.header(question["question"], divider="rainbow")
            # We're not showing the topic for coding questions since they're generated without a topic constraint
            st.write("###### Difficulty Level: " + question["difficulty"])
            
            # Use tabs to organize content and reduce page size
            problem_tab, solution_tab = st.tabs(["Problem", "Solution"])
            
            with problem_tab:
                # Display problem description and requirements
                st.markdown("### Problem Description")
                st.markdown(question["description"])
                
                if "examples" in question and question["examples"]:
                    st.markdown("### Examples")
                    st.markdown(question["examples"])
                
                # Language selection for code editor
                language = question.get("language", "python").lower()
                
                # Code editor for a better coding experience
                st.markdown("### Your Solution")
                
                # Get theme based on light/dark mode if supported
                theme = "light" if st.get_option("theme.base") == "light" else "dark"
                
                # Prevent recomputing editor unless needed using st.cache_data which helps reduce reruns
                @st.cache_data(show_spinner=False)
                def get_editor_options():
                    return {"showLineNumbers": True, 
                           "highlightActiveLine": True, 
                           "tabSize": 4}
                
                # Optimize code editor parameters
                user_code = code_editor(st.session_state.user_code_input,
                                        lang='python', 
                                        theme="default", 
                                        shortcuts="vscode", 
                                        height=30, 
                                        focus=False, 
                                        allow_reset=False,
                                        options=get_editor_options()
                )
                
                # Only update if code actually changed (reduces reruns)
                if user_code != st.session_state.user_code_input:
                    st.session_state.user_code_input = user_code
            
            with solution_tab:
                if not st.session_state.coding_answered:
                    st.info("Click 'Show Solution' to view the solution")
                else:
                    st.markdown("### Solution")
                    st.markdown(question["solution"])
                    
                    if "code_solution" in question and question["code_solution"]:
                        st.markdown("### Code Solution")
                        
                        # Display solution code with syntax highlighting
                        st.code(question["code_solution"], language=language)
                    
                    st.markdown("### Explanation")
                    st.markdown(question["explanation"])
            
            col1, col2 = st.columns(2)
            
            # Submit button logic
            with col1:
                if st.button("Show Solution", key="coding_solution_button") and not st.session_state.coding_answered:
                    st.session_state.coding_answered = True
                    # Force a rerun to show solution tab
                    st.experimental_rerun()

            # Next button logic
            with col2:
                if st.button("Next Question", key="coding_next_button", on_click=load_new_coding_question):
                    pass


def load_new_coding_question():
    """
    Load a new coding interview question based only on the difficulty level.
    """
    # Show a spinner while loading
    with st.spinner("Loading new question..."):
        # Store the current topic for display purposes only
        topic = get_random_topic()
        st.session_state.coding_current_topic = topic
        
        try:
            # Note: We're now passing None as the topic, as we don't want to constrain by topic
            question_data = generate_coding_question(None, st.session_state.difficulty)
            st.session_state.coding_question_data = json.loads(question_data)
            st.session_state.coding_current_question_id += 1
            
            # Initialize code input with starter code if available
            if "starter_code" in st.session_state.coding_question_data and st.session_state.coding_question_data["starter_code"]:
                st.session_state.user_code_input = st.session_state.coding_question_data["starter_code"]
            else:
                # Provide a basic template based on the language
                language = st.session_state.coding_question_data.get("language", "python").lower()
                if language == "python":
                    st.session_state.user_code_input = "# Write your Python solution here\n\ndef solution(input):\n    # Your code here\n    pass\n\n# Test your solution\nif __name__ == \"__main__\":\n    # Add test cases here\n    pass"
                else:
                    st.session_state.user_code_input = "# Write your solution here"
            
            st.session_state.coding_answered = False
            st.session_state.coding_question_version += 1  # Increment version to refresh widgets
            
        except Exception as e:
            st.error(f"Failed to generate question: {str(e)}")
            st.session_state.coding_question_data = None


if __name__ == "__main__":
    main() 