"""
Main application module for DeepMindset.ai

This module contains the main application logic for the DeepMindset.ai application.
It handles the UI setup, navigation, and interaction with the various components.
"""
import streamlit as st
import json
import torch

from src.services.question_service import generate_mcq_question, generate_subjective_question
from src.services.topic_service import update_topics, get_random_topic
from src.services.answer_service import get_gpt_answer
from src.config.app_config import setup_page_config

# Fix for torch classes path issue
torch.classes.__path__ = []  # Manually set it to empty


def main():
    """
    Main application function that sets up the Streamlit UI and handles user interactions.
    """
    # Set page configuration
    setup_page_config()

    # Set up the main layout with title
    st.title("DeepMindset.ai")

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

    # Right sidebar for quick search
    with right_sidebar:
        render_search_sidebar()


def setup_navigation():
    """
    Set up the navigation sidebar with buttons for different pages.
    """
    st.sidebar.title("Navigation")

    # Initialize session state for current page if not set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "MCQ"  # Default landing page

    # Create navigation buttons
    if st.sidebar.button("MCQ", key="quiz_btn", use_container_width=True):
        st.session_state.current_page = "MCQ"
    if st.sidebar.button("Subjectives", key="subjectives_btn", use_container_width=True):
        st.session_state.current_page = "Subjectives"
    if st.sidebar.button("Update Topics", key="update_topics_btn", use_container_width=True):
        st.session_state.current_page = "Update Topics"

    # Highlight the current page
    st.sidebar.markdown(f"**Current page:** {st.session_state.current_page}")

    # Add quiz settings to sidebar when on quiz pages
    if st.session_state.current_page in ["MCQ", "Subjectives"]:
        st.sidebar.markdown("---")  # Add separator
        st.sidebar.markdown("### Quiz Settings")
        # Difficulty dropdown and stay on topic checkbox
        st.session_state.difficulty = st.sidebar.selectbox(
            "Select Difficulty", 
            ["Easy", "Medium", "Hard", "Expert"],
            key="difficulty_selector"
        )
        st.session_state.stay_topic = st.sidebar.checkbox(
            "Stay on same topic", 
            key="stay_topic", 
            value=False
        )


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
    Render the MCQ quiz page.
    """
    # Initialize session state variables for MCQ if not set already
    if "mcq_question_data" not in st.session_state:
        st.session_state.mcq_question_data = None
    if "mcq_answered" not in st.session_state:
        st.session_state.mcq_answered = False
    if "mcq_score" not in st.session_state:
        st.session_state.mcq_score = 0
    if "mcq_current_topic" not in st.session_state:
        st.session_state.mcq_current_topic = None
    if "mcq_current_question_id" not in st.session_state:
        st.session_state.mcq_current_question_id = 0
    if "mcq_question_version" not in st.session_state:
        st.session_state.mcq_question_version = 0
    if "mcq_selected_options" not in st.session_state:
        st.session_state.mcq_selected_options = []

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
                st.button("Next Question", key="mcq_next_button", on_click=load_new_mcq_question)

    st.write("### Your Score:", st.session_state.mcq_score)


def load_new_mcq_question():
    """
    Load a new MCQ question based on the current settings.
    """
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
    Render the subjective questions page.
    """
    # Initialize session state variables for Subjectives if not set already
    if "subj_question_data" not in st.session_state:
        st.session_state.subj_question_data = None
    if "subj_answered" not in st.session_state:
        st.session_state.subj_answered = False
    if "subj_current_topic" not in st.session_state:
        st.session_state.subj_current_topic = None
    if "subj_current_question_id" not in st.session_state:
        st.session_state.subj_current_question_id = 0
    if "subj_question_version" not in st.session_state:
        st.session_state.subj_question_version = 0

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
            st.button("Next Question", key="subj_next_button", on_click=load_new_subjective_question)


def load_new_subjective_question():
    """
    Load a new subjective question based on the current settings.
    """
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
    Render the quick search sidebar.
    """
    st.markdown("### Quick Search")
    st.write("Ask any question and get a quick answer.")
    
    # Initialize session state for search history
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    
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


if __name__ == "__main__":
    main() 