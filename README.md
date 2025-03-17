# DeepMindset.ai

A Streamlit-based chat quiz application that leverages Retrieval-Augmented Generation (RAG).

## Features

- **Multiple-Choice Questions (MCQ)**: Generate random quizzes from your knowledge base with varying difficulty levels.
- **Subjective Questions**: Test your knowledge with open-ended questions.
- **Topic Management**: Organize your knowledge base with hierarchical topics.
- **Quick Search**: Ask any question and get an instant answer from GPT.

## Architecture

DeepMindset.ai follows a modular architecture pattern:

- **Services**: Core business logic for generating questions, retrieving topics, and providing answers.
- **Models**: Data models for representing questions and other entities.
- **Config**: Application configuration management.
- **Utils**: Utility functions for error handling, logging, and other common tasks.

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setting Up

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/deepmindset.ai.git
   cd deepmindset.ai
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   - Copy `.env.example` to `.env` and fill in your OpenAI API key
   - Or set up Streamlit secrets by creating `.streamlit/secrets.toml` with:
     ```toml
     [openai]
     api_key = "your-openai-api-key"
     ```

## Running the Application

### Local Development

```bash
streamlit run app.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Adding Topics

1. Create text files in the `topic_store/raw/` directory with indented hierarchies:

   ```
   Main Topic
       Subtopic 1
           Sub-subtopic A
       Subtopic 2
   ```

2. Use the "Update Topics" feature in the application to process these files.

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## Project Structure

```
deepmindset.ai/
├── app.py                  # Main entry point
├── src/                    # Source code
│   ├── app.py              # Main application logic
│   ├── config/             # Configuration
│   ├── models/             # Data models
│   ├── services/           # Core services
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── topic_store/            # Topic storage
│   ├── raw/                # Raw topic files
│   └── topics/             # Processed topic JSON
├── logs/                   # Application logs
├── .streamlit/             # Streamlit configuration
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
