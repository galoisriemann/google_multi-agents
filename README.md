# Workflow Google ADK

A production-ready sequential workflow system using Google's Agent Development Kit (ADK) for code generation, review, refactoring, and RAG (Retrieval-Augmented Generation) operations with MCP (Model Context Protocol) integration.

## Features

### Core Workflow System
- **Sequential Workflow**: Three-agent pipeline (CodeWriter → CodeReviewer → CodeRefactorer)
- **Google ADK Integration**: Native Google ADK support with Gemini models
- **Configurable**: YAML-based configuration for workflows and prompts
- **Production Ready**: Comprehensive error handling, logging, and security
- **Type Safe**: Full type annotations with mypy compatibility
- **Async Support**: Asynchronous workflow processing

### RAG Workflow with MCP Integration
- **Dual MCP Integration**: Support for Google ADK MCPToolset and direct MCP protocol calls
- **Tool-based MCP**: Modern tool-based approach using Google ADK MCPToolset
- **Security Features**: Built-in tool filtering and access control
- **Automatic Fallback**: Robust error handling with fallback mechanisms
- **Scalable Architecture**: Easy integration of multiple MCP servers and tools

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

#### Basic Workflow System
```bash
# Activate the environment
poetry shell

# Run the code generation workflow
python backend/main.py
```

#### RAG Workflow with MCP
```bash
# Run RAG workflow with Google ADK MCPToolset (recommended)
python backend/main_rag.py

# Run with specific tools
python backend/main_rag.py --allowed-tools get_generative_search_response search_documents

# Run with custom query
python backend/main_rag.py --query "What are the latest AI developments?"

# Run with custom system prompt
python backend/main_rag.py --system-prompt "You are a financial advisor expert."
```

## Project Structure

```
workflow_google/
├── backend/
│   ├── main.py                    # Main workflow entry point
│   ├── main_rag.py               # RAG workflow entry point
│   ├── workflow_manager.py        # Core workflow logic
│   ├── workflow_manager_rag.py    # RAG workflow with MCP integration
│   ├── data_model/
│   │   └── data_models.py         # Pydantic data models
│   ├── config/
│   │   ├── workflow_config.yml    # Main workflow configuration
│   │   ├── workflow_rag.yml       # RAG workflow configuration
│   │   └── gemini_config.yml      # LLM configuration (includes API key)
│   ├── prompts/
│   │   ├── prompts.yml            # Main workflow prompt templates
│   │   └── prompts_rag.yml        # RAG workflow prompt templates
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

#### Main Workflow Configuration (`backend/config/workflow_config.yml`)

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

#### RAG Workflow Configuration (`backend/config/workflow_rag.yml`)

```yaml
name: "RAG Workflow"
description: "RAG workflow using Google ADK MCPToolset"
version: "2.0.0"

# MCP Integration Configuration
mcp_config:
  default_mode: "adk_toolset"
  
  # ADK Toolset Configuration
  adk_toolset:
    allowed_tools:
      - "get_generative_search_response"
      - "search_documents"
      - "retrieve_context"
      - "generate_answer"
    sse_endpoint_suffix: "/sse"
    agent:
      model: "gemini-2.0-flash"
      name: "rag_assistant"

steps:
  - name: "RAGAgent"
    model: "gemini-2.0-flash"
    prompt_key: "rag_query"
    description: "Performs RAG operations using MCP tools"
    tools:
      - name: "mcp_tool"
        type: "mcp"
        config:
          mcp_endpoint: "http://localhost:8000/mcp"
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

### Prompts Configuration

#### Main Workflow Prompts (`backend/prompts/prompts.yml`)

```yaml
version: "1.0.0"
prompts:
  code_writer: |
    Write a Python implementation for the following specification:
    {prompt}
    # ... rest of prompt
```

#### RAG Workflow Prompts (`backend/prompts/prompts_rag.yml`)

```yaml
version: "1.0.0"
prompts:
  rag_query: |
    You are an expert research assistant. Search for and provide comprehensive information about:
    {query}
    # ... rest of prompt
```

## MCP Integration Architecture

The RAG workflow system supports Google ADK MCPToolset integration:

```
RAGWorkflowManager
└── ADK Toolset Mode
    ├── LlmAgent with MCPToolset
    ├── SSE-based communication
    ├── Tool filtering and security
    └── Comprehensive error handling
```

### MCP Integration Features

**Google ADK MCPToolset Mode:**
- ✅ **Tool-based approach**: Seamless integration with Google ADK agent framework
- ✅ **Security**: Built-in tool filtering and access control
- ✅ **Scalability**: Easy integration of multiple MCP servers and tools
- ✅ **Error handling**: Robust error handling mechanisms
- ✅ **Type safety**: Strong typing and validation
- ✅ **Monitoring**: Built-in logging and debugging capabilities

### MCP Usage Examples

#### Basic RAG Query
```python
from workflow_manager_rag import RAGWorkflowManager, WorkflowPaths, ConfigLoader

# Initialize components
paths = WorkflowPaths()
config_loader = ConfigLoader(paths)

# Create RAG workflow manager
workflow_manager = RAGWorkflowManager(
    config_loader=config_loader,
    allowed_tools=["get_generative_search_response"]
)

# Run the workflow
result = await workflow_manager.run({
    "query": "What are the latest AI developments?",
    "system_prompt": "You are an expert research assistant."
})
```

#### Production Setup
```python
import os
from typing import Optional

class ProductionRAGManager:
    def __init__(self, allowed_tools: Optional[list] = None):
        # Production-ready tool filtering
        self.production_tools = allowed_tools or [
            "get_generative_search_response",
            "search_documents",
            "retrieve_context"
        ]
        
        # Initialize with production settings
        self.workflow_manager = RAGWorkflowManager(
            config_loader=self.config_loader,
            allowed_tools=self.production_tools
        )
    
    async def process_query(self, query: str, user_context: dict) -> dict:
        """Process query with production-ready error handling."""
        input_data = {
            "query": query,
            "system_prompt": self._build_system_prompt(user_context),
            "metadata": {
                "user_id": user_context.get("user_id"),
                "session_id": user_context.get("session_id"),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return await self.workflow_manager.run(input_data)
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
- **Tool Filtering**: Control which MCP tools are accessible to agents
- **Access Control**: Built-in security mechanisms for MCP integration
- **Clear Error Messages**: Helpful guidance when configuration is missing
- **Git Safety**: Use `.gitignore` to exclude sensitive files if needed

## Production Deployment

1. **For YAML-based deployment**: Ensure API keys are in configuration files
2. **For container deployment**: Use environment variables
3. Set `LOG_LEVEL=INFO` in production
4. Configure proper API rate limits
5. Set up monitoring and error tracking
6. **For MCP integration**: Ensure MCP servers are properly secured and accessible

## Dependencies

### Core Dependencies
- **google-adk**: Google Agent Development Kit
- **google-ai-generativelanguage**: Google Generative AI client
- **pydantic**: Data validation and settings
- **pyyaml**: YAML configuration parsing
- **python-dotenv**: Environment variable management

### Development Dependencies
- **pytest**: Testing framework
- **ruff**: Code formatting and linting
- **mypy**: Type checking

## License

MIT License 