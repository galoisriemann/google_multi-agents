# Workflow System

A flexible workflow system for building and managing research agents with Google's Agent Development Kit (ADK).

## Project Structure

```
backend/
├── core/                      # Core functionality shared across the application
│   ├── __init__.py
│   ├── agents/                # Base agent implementations
│   │   ├── __init__.py
│   │   └── base_agent.py      # BaseResearchAgent class
│   ├── config/                # Configuration handling
│   │   ├── __init__.py
│   │   └── config_loader.py   # Configuration loading and validation
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── common.py          # Common utilities
│       └── response_formatter.py # Response formatting utilities
├── main.py                    # Main entry point
└── main_rag_deepresearch.py   # RAG-based research agent implementation
```

## Core Components

### BaseResearchAgent

The `BaseResearchAgent` class provides a foundation for building research agents with:
- Configuration management
- Session handling
- Tool integration
- Response formatting
- Error handling

### Configuration

Configuration is managed through YAML files with support for:
- Nested configuration using dot notation
- Required field validation
- Environment variable overrides

### Response Formatting

The `response_formatter` module provides utilities for formatting agent responses with:
- Source citations
- Tool usage information
- Error handling
- Metadata inclusion

## Usage

### Creating a New Agent

1. Create a new Python file for your agent
2. Subclass `BaseResearchAgent`
3. Implement required methods:
   - `get_tools()`: Return a list of tools the agent can use
   - `get_agent_instruction()`: Return the agent's instruction prompt
   - `process_events()`: Handle agent execution events

Example:

```python
from core.agents.base_agent import BaseResearchAgent

class MyResearchAgent(BaseResearchAgent):
    def get_tools(self):
        # Return list of tools
        pass
        
    def get_agent_instruction(self):
        # Return agent instruction
        pass
        
    async def process_events(self, events):
        # Process agent events
        pass
```

### Running an Agent

```python
agent = MyResearchAgent(
    config_path="path/to/config.yml",
    prompts_path="path/to/prompts.yml",
    agent_name="My Agent",
    agent_description="A research agent for my specific needs"
)

# Run a query
response = await agent.query("Your research question here")
print(response["content"])
```

## Configuration

### Required Configuration

```yaml
# config.yml
example:
  core_config:
    model: "gemini-1.5-pro"
    api_key: ${GOOGLE_API_KEY}  # Can use environment variables
    
  app_config:
    app_name: "research_agent"
    user_id: "user1"
    session_id: "session1"
```

### Prompts

Prompts are loaded from YAML files with the following structure:

```yaml
# prompts.yml
category_name:
  template_name: |
    This is a template with {variables}.
    You can use {variables} in your templates.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
