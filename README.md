# Workflow Google ADK

A production-ready sequential workflow system using Google's Agent Development Kit (ADK) for code generation, review, and refactoring.

## Features

- **Sequential Workflow**: Three-agent pipeline (CodeWriter → CodeReviewer → CodeRefactorer)
- **Google ADK Integration**: Native Google ADK support with Gemini models
- **Configurable**: YAML-based configuration for workflows and prompts
- **Production Ready**: Comprehensive error handling, logging, and security
- **Type Safe**: Full type annotations with mypy compatibility
- **Async Support**: Asynchronous workflow processing

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Google API key for Gemini models

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workflow_google
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Configure API Key**
   
   **Option 1: YAML Configuration (Recommended)**
   - Edit `backend/config/gemini_config.yml`
   - Add your API key to the `api_config.api_key` field

   **Option 2: Environment Variable (Fallback)**
   ```bash
   cp env.example .env
   # Edit .env and uncomment GOOGLE_API_KEY
   export GOOGLE_API_KEY=your_actual_api_key_here
   ```

4. **Get Google API Key**
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Create an API key
   - Add it to your configuration (see step 3)

### Usage

```bash
# Activate the environment
poetry shell

# Run the workflow
python backend/main.py
```

## Project Structure

```
workflow_google/
├── backend/
│   ├── main.py                    # Main entry point
│   ├── workflow_manager.py        # Core workflow logic
│   ├── data_model/
│   │   └── data_models.py         # Pydantic data models
│   ├── config/
│   │   ├── workflow_config.yml    # Workflow configuration
│   │   └── gemini_config.yml      # LLM configuration (includes API key)
│   ├── prompts/
│   │   └── prompts.yml            # Prompt templates
│   ├── input/                     # Input directory (auto-created)
│   └── output/                    # Output directory (auto-created)
├── tests/
│   ├── test_workflow.py           # Workflow tests
│   └── test_gemini_provider.py    # Provider tests
├── pyproject.toml                 # Poetry configuration
├── env.example                    # Environment variable template (optional)
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## Configuration

### Primary Configuration: YAML Files

#### Workflow Configuration (`backend/config/workflow_config.yml`)

```yaml
name: "Code Generation Pipeline"
description: "A sequential workflow for generating, reviewing, and refactoring code"
version: "1.0.0"

api_config:
  provider: "gemini"
  model: "gemini-1.5-flash"
  temperature: 0.0
  max_tokens: 2048
  timeout: 60

steps:
  - name: "CodeWriterAgent"
    model: "gemini-1.5-flash"
    prompt_key: "code_writer"
    description: "Writes initial Python code"
    # ... more configuration
```

#### LLM Configuration (`backend/config/gemini_config.yml`)

```yaml
provider: "gemini"
model: "gemini-1.5-flash"
temperature: 0.0
max_tokens: 2048

api_config:
  api_key: "your_google_api_key_here"  # Alternative API key location
  timeout: 60
```

### Fallback Configuration: Environment Variables

If no API key is found in YAML files, the system will check for:
```bash
export GOOGLE_API_KEY=your_api_key_here
```

### Prompts Configuration (`backend/prompts/prompts.yml`)

Define prompt templates for each agent:

```yaml
version: "1.0.0"
prompts:
  code_writer: |
    Write a Python implementation for the following specification:
    {prompt}
    # ... rest of prompt
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Quality

```bash
# Linting and formatting
poetry run ruff check .
poetry run ruff format .

# Type checking
poetry run mypy backend/
```

## Configuration Priority

The system loads configuration in this order:

1. **YAML Configuration** (Primary): API key from `gemini_config.yml`
2. **Environment Variables** (Fallback): `GOOGLE_API_KEY` environment variable
3. **Error**: If neither is found, the system will raise a clear error message

## Security

- **Flexible Configuration**: Choose between YAML or environment variables
- **Clear Error Messages**: Helpful guidance when configuration is missing
- **Git Safety**: Use `.gitignore` to exclude sensitive files if needed

## Production Deployment

1. **For YAML-based deployment**: Ensure API keys are in configuration files
2. **For container deployment**: Use environment variables
3. Set `LOG_LEVEL=INFO` in production
4. Configure proper API rate limits
5. Set up monitoring and error tracking

## Dependencies

- **google-adk**: Google Agent Development Kit
- **google-ai-generativelanguage**: Google Generative AI client
- **pydantic**: Data validation and settings
- **pyyaml**: YAML configuration parsing
- **python-dotenv**: Environment variable management

## License

MIT License 