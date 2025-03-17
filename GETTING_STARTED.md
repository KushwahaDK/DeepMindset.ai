# Getting Started with DeepMindset.ai

This guide will help you set up and start using DeepMindset.ai for your learning needs.

## Initial Setup

1. **Install the Requirements**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Your OpenAI API Key**

   There are two ways to set up your API key:

   - **Option 1**: Create a `.streamlit/secrets.toml` file with:
     ```toml
     [openai]
     api_key = "your-openai-api-key"
     ```

   - **Option 2**: Create a `.env` file with:
     ```
     OPENAI_API_KEY=your-openai-api-key
     ```

3. **Create Your Topics**

   DeepMindset.ai uses a hierarchical topic structure:

   - Create text files in the `topic_store/raw/` directory
   - Use indentation to define the hierarchy of topics
   - For example:
     ```
     Main Topic
         Subtopic 1
             Sub-subtopic A
         Subtopic 2
     ```

## Running the Application

```bash
streamlit run app.py
```

## Features Overview

### MCQ (Multiple Choice Questions)

The MCQ feature generates multiple-choice questions based on your topics:

1. Navigate to the MCQ page from the sidebar
2. Select the difficulty level from Easy to Expert
3. Check "Stay on same topic" if you want multiple questions on the same topic
4. Answer the question and click "Submit" to check your answer
5. Click "Next Question" to continue

### Subjective Questions

The Subjective Questions feature generates open-ended questions:

1. Navigate to the Subjective page from the sidebar
2. Select the difficulty level
3. Read the question and think about your answer
4. Click "Show Answer" to see the explanation
5. Click "Next Question" to continue

### Update Topics

Use this page to process your raw topic files:

1. Navigate to the Update Topics page
2. Click the "Update Topics" button
3. The system will scan your `topic_store/raw/` directory and create JSON files in `topic_store/topics/`

### Quick Search

The Quick Search sidebar lets you ask any question:

1. Type your question in the text area
2. Click "Ask" to get an answer from GPT
3. Your recent questions and answers will appear below

## Tips for Best Results

1. **Organized Topic Hierarchy**: Create a well-structured topic hierarchy for better question generation
2. **Regular Updates**: Update your topics regularly to keep content fresh
3. **Difficulty Progression**: Start with Easy questions and gradually increase difficulty
4. **Topic Focus**: Use the "Stay on same topic" option to deep dive into a specific topic

## Troubleshooting

If you encounter any issues:

- Check your API key is correctly set up
- Ensure your topic files are properly formatted with consistent indentation
- Look at the logs in the `logs/` directory for detailed error messages
- Make sure you have an active internet connection for OpenAI API calls

## Next Steps

After you're comfortable with the basics, consider:

- Adding more topic files to expand your knowledge base
- Customizing the codebase to add new features
- Contributing to the open-source repository 