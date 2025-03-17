# main.py
import torch
import streamlit as st
import json
from openai import OpenAI

# Set page configuration to wide layout
st.set_page_config(layout="wide")

from question_generator import generate_mcq_question, generate_subjective_question
from topic_generator import update_topics
from topic_retriever import get_random_topic
torch.classes.__path__ = [] # add this line to manually set it to empty.

# Function to process raw text
def process_raw_text(text):
    # Split text into chunks and store in the same format as URL content
    return [text]

# Function to get answer from GPT model
def get_gpt_answer(question):
    try:
        client = OpenAI(api_key=st.secrets["openai"]["api_key"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing concise answers to questions about any topic."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Set up the main layout with columns
st.title("DeepMindset.ai")

# Create a layout with main content and right sidebar
main_col, right_sidebar = st.columns([3, 1], gap="medium")

with main_col:
    # Create a sidebar for navigation with selectable options instead of radio buttons
    st.sidebar.title("Navigation")

    # Use buttons in the sidebar for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "MCQ"  # Set default landing page to MCQ

    # Create full-width selectable buttons
    if st.sidebar.button("MCQ", key="quiz_btn", use_container_width=True):
        st.session_state.current_page = "MCQ"
    if st.sidebar.button("Subjectives", key="subjectives_btn", use_container_width=True):
        st.session_state.current_page = "Subjectives"
    if st.sidebar.button("Update Topics", key="update_topics_btn", use_container_width=True):
        st.session_state.current_page = "Update Topics"

    # Highlight the current page
    st.sidebar.markdown(f"**Current page:** {st.session_state.current_page}")

    # Move Quiz settings to sidebar when MCQ or Subjectives page is selected
    if st.session_state.current_page in ["MCQ", "Subjectives"]:
        st.sidebar.markdown("---")  # Add a separator
        st.sidebar.markdown("### Quiz Settings")
        difficulty = st.sidebar.selectbox("Select Difficulty", ["Easy", "Medium", "Hard", "Expert"])
        stay_topic = st.sidebar.checkbox("Stay on same topic", key="stay_topic", value=False)

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

    if st.session_state.current_page == "Update Topics":
        st.header("Update Topics")
        
        st.write("This will scan the topic_store/raw directory for new topic files and generate JSON files in the topic_store/topics directory.")
        
        if st.button("Update Topics", key="update_topics_button"):
            with st.spinner("Updating topics..."):
                result = update_topics()
                if result:
                    st.success("Topics updated successfully!")
                else:
                    st.error("Failed to update topics. Please check the logs for more information.")

    elif st.session_state.current_page == "MCQ":
        def load_new_mcq_question():
            if stay_topic:
                topic = st.session_state.mcq_current_topic
                if not topic:
                    topic = get_random_topic()
                    st.session_state.mcq_current_topic = topic
            else:
                topic = get_random_topic()
                st.session_state.mcq_current_topic = topic
            
            question_data = generate_mcq_question(topic, difficulty)
            try:
                st.session_state.mcq_question_data = json.loads(question_data)
                st.session_state.mcq_current_question_id += 1
                st.session_state.mcq_selected_options = []  # Reset selected options
                st.session_state.mcq_answered = False
                st.session_state.mcq_question_version += 1  # Increment version to refresh widgets
            except Exception as e:
                st.error("Failed to generate question. Please try again.")
                st.session_state.mcq_question_data = None

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
                        st.write("Correct Answers: " + ", ".join(correct_options))  # Show correct answers
                        st.session_state.mcq_score += 1
                    else:
                        st.error("Wrong Answer!")
                        st.write("Correct Answers: " + ", ".join(correct_options))  # Show correct answers
                    st.write("**Explanation:** " + question["explanation"])
                    st.session_state.mcq_answered = True

                # Next button logic
                if st.session_state.mcq_answered:  # Show "Next" only after answering
                    st.button("Next Question", key="mcq_next_button", on_click=load_new_mcq_question)

        st.write("### Your Score:", st.session_state.mcq_score)

    elif st.session_state.current_page == "Subjectives":
        def load_new_subjective_question():
            if stay_topic:
                topic = st.session_state.subj_current_topic
                if not topic:
                    topic = get_random_topic()
                    st.session_state.subj_current_topic = topic
            else:
                topic = get_random_topic()
                st.session_state.subj_current_topic = topic
            
            question_data = generate_subjective_question(topic, difficulty)
            try:
                st.session_state.subj_question_data = json.loads(question_data)
                st.session_state.subj_current_question_id += 1
                st.session_state.subj_answered = False
                st.session_state.subj_question_version += 1  # Increment version to refresh widgets
            except Exception as e:
                st.error("Failed to generate question. Please try again.")
                st.session_state.subj_question_data = None

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
                # if st.session_state.subj_answered:  # Show "Next" only after answering
                st.button("Next Question", key="subj_next_button", on_click=load_new_subjective_question)

# Right sidebar for quick search
with right_sidebar:
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
