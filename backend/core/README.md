# Flexible Agent Core Modules

This directory contains the core modular components for the flexible agent workflow system. The original `flexible_agent.py` has been refactored into reusable, well-organized modules.

## 📁 Directory Structure

```
backend/core/
├── agents/                          # Agent-related components
│   ├── __init__.py                 # Agent module exports
│   ├── flexible_agent_factory.py   # Factory for creating agents
│   └── flexible_loop_checker.py    # Loop termination agent
├── config/                          # Configuration components
│   ├── __init__.py
│   ├── config_loader.py            # Configuration loading utilities
│   └── flexible_config.py          # Pydantic models for workflow config
├── tools/                           # Tool registry and implementations
│   ├── __init__.py                 # Tool module exports
│   └── tool_registry.py           # Tool registry and example tools
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── common.py                   # Common utilities
│   ├── document_reader.py          # Document processing
│   ├── file_utils.py              # File operations
│   └── response_formatter.py       # Response formatting
└── workflow/                        # Workflow management
    ├── __init__.py                 # Workflow module exports
    └── flexible_workflow_manager.py # Main workflow orchestrator
```

## 🔧 Core Components

### Configuration Models (`config/flexible_config.py`)
- **FlexibleAgentConfig**: Configuration for individual agents
- **FlexibleWorkflowConfig**: Configuration for entire workflows

### Tool Registry (`tools/tool_registry.py`)
- **FlexibleToolRegistry**: Centralized tool registration and retrieval
- **Example Tools**: text_processor, text_analyzer, code_formatter, data_validator

### Agent Factory (`agents/flexible_agent_factory.py`)
- **FlexibleAgentFactory**: Creates and configures agents from configuration
- **FLEXIBLE_AGENT_CLASSES**: Mapping of agent types to classes
- Supports incremental output saving and document injection

### Loop Checker (`agents/flexible_loop_checker.py`)
- **FlexibleLoopChecker**: Specialized agent for loop termination conditions
- Configurable stop keywords and conditions

### Workflow Manager (`workflow/flexible_workflow_manager.py`)
- **FlexibleWorkflowManager**: Main orchestrator for flexible workflows
- Handles initialization, execution, error reporting, and result saving
- Supports incremental output saving and comprehensive reporting

## 🚀 Usage Examples

### Basic Usage

```python
from backend.core.workflow import FlexibleWorkflowManager
from backend.core.tools import FlexibleToolRegistry

# Create workflow manager
workflow_manager = FlexibleWorkflowManager()

# Run a workflow
result = await workflow_manager.run_workflow("Your request here")
```

### Custom Tool Registration

```python
from backend.core.tools import FlexibleToolRegistry

@FlexibleToolRegistry.register
def custom_tool(input_data: str) -> str:
    """Custom tool implementation."""
    return f"Processed: {input_data}"

# Tool is now available to all agents
```

### Direct Agent Factory Usage

```python
from backend.core.agents import FlexibleAgentFactory
from backend.core.config import FlexibleAgentConfig

# Create agent configurations
configs = [
    FlexibleAgentConfig(
        name="MyAgent",
        type="LlmAgent",
        model="gemini-1.5-flash",
        prompt_key="my_prompt"
    )
]

# Create factory and build agents
factory = FlexibleAgentFactory(configs, prompts_loader, input_dir)
agents = factory.build_all()
```

## ✨ Benefits of Modular Design

1. **Reusability**: Components can be imported and used independently
2. **Maintainability**: Each module has a single responsibility
3. **Testability**: Individual components can be tested in isolation
4. **Extensibility**: Easy to add new tools, agents, or configurations
5. **Documentation**: Clear separation of concerns and API boundaries

## 🔄 Migration from Original Code

The original `flexible_agent.py` (1404 lines) has been refactored into:
- **Config Models**: 60 lines
- **Tool Registry**: 150 lines  
- **Loop Checker**: 70 lines
- **Agent Factory**: 370 lines
- **Workflow Manager**: 895 lines
- **Main Module**: 95 lines

Total reduction of ~154 lines with improved organization and reusability.

## 🛠️ Development Guidelines

When extending the flexible agent system:

1. **New Tools**: Add to `tools/tool_registry.py` with `@FlexibleToolRegistry.register`
2. **New Agent Types**: Extend `FLEXIBLE_AGENT_CLASSES` in `agent_factory.py`
3. **New Config Fields**: Update Pydantic models in `config/flexible_config.py`
4. **New Utilities**: Add to appropriate module in `utils/`
5. **Workflow Extensions**: Extend `FlexibleWorkflowManager` in `workflow/`

## 📝 Import Guidelines

From project root:
```python
from backend.core.workflow import FlexibleWorkflowManager
from backend.core.tools import FlexibleToolRegistry
from backend.core.config import FlexibleAgentConfig, FlexibleWorkflowConfig
```

From within modules, imports are handled automatically with fallbacks for both absolute and relative import patterns. 