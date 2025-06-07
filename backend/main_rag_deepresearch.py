import os
import sys
import yaml
import asyncio

# Add project root to Python path for direct execution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search  # Built-in ADK tool
from google.genai import types

from backend.tools.deep_research_tool import deep_research_function_tool


# ---- CONFIG LOADING ----

WORKFLOW_CONFIG_PATH = "backend/config/workflow_deepresearch.yml"

def load_workflow_config(path: str) -> dict:
    """Load workflow configuration from YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_config_value(config: dict, key_path: str, default=None):
    """Get nested configuration value using dot notation (e.g. 'api_config.model')."""
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value

def validate_config(config: dict):
    """Validate that required configuration values are present."""
    required_keys = [
        "api_config.model",
        "app_config.app_name",
        "mcp_config.rag_mcp_endpoint",
        "gemini_config.api_key"
    ]
    
    missing_keys = []
    for key_path in required_keys:
        if get_config_value(config, key_path) is None:
            missing_keys.append(key_path)
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

# Load configuration
workflow_config = load_workflow_config(WORKFLOW_CONFIG_PATH)

# Validate configuration
validate_config(workflow_config)

# Extract configuration values
MODEL_ID = get_config_value(workflow_config, "api_config.model")
APP_NAME = get_config_value(workflow_config, "app_config.app_name")
USER_ID = get_config_value(workflow_config, "app_config.user_id")
SESSION_ID = get_config_value(workflow_config, "app_config.session_id")
RAG_MCP_ENDPOINT = get_config_value(workflow_config, "mcp_config.rag_mcp_endpoint")
API_KEY = get_config_value(workflow_config, "gemini_config.api_key")

# Set Google API key as environment variable (ADK expects this)
if API_KEY:
    os.environ['GOOGLE_API_KEY'] = API_KEY

# Extract Gemini configuration
gemini_config = workflow_config.get("gemini_config", {})

# Extract agent configuration
agent_config = get_config_value(workflow_config, "mcp_config.adk_toolset.agent", {})
AGENT_NAME = agent_config.get("name", "deep_research_agent")
AGENT_DESCRIPTION = agent_config.get("description", "Agent for deep/agentic research")
AGENT_INSTRUCTION = agent_config.get("instruction_template", "Use tools to perform research.")

# ---- AGENT WRAPPER ----

class DeepResearchAgent:
    """Wrapper for the ADK Agent that handles configuration and session management."""
    
    def __init__(self):
        self.config = workflow_config
        self.runner = None
        self.session = None
        
    async def _init_runner(self):
        """Initialize the ADK runner and session with configuration."""
        if self.runner is not None:
            return  # Already initialized
            
        # Create agent with tools (API key is set via environment variable)
        agent = Agent(
            name=AGENT_NAME,
            model=MODEL_ID,
            description=AGENT_DESCRIPTION,
            instruction=AGENT_INSTRUCTION,
            tools=[
                deep_research_function_tool  # Custom RAG workflow tool
                # Note: google_search removed due to Gemini 1.x limitation with multiple tools
            ]
        )
        
        # Setup runner 
        self.runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
        
        # Create session with initial state containing our configuration
        initial_state = {
            "workflow_config": self.config,
            "deep_research_config": self.config.get("deep_research_config", {}),
            "gemini_config": self.config.get("gemini_config", {}),
            "rag_mcp_endpoint": RAG_MCP_ENDPOINT
        }
        
        # Create session with configuration in initial state
        self.session = await self.runner.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            state=initial_state
        )

    async def query_async(self, query: str) -> str:
        """Query the agent asynchronously."""
        await self._init_runner()
        
        # Create content for the query
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent and collect events
        events = self.runner.run_async(
            user_id=self.session.user_id,
            session_id=self.session.id,
            new_message=content
        )
        
        # Process events and return the final response
        final_response = None
        async for event in events:
            if hasattr(event, 'is_final_response') and event.is_final_response():
                final_response = event.content.parts[0].text
                break
            elif hasattr(event, 'content') and event.content:
                # Fallback for different event types
                if hasattr(event.content, 'parts') and event.content.parts:
                    final_response = event.content.parts[0].text
        
        return final_response or "No response received from agent"

    def query(self, query: str) -> str:
        """Query the agent synchronously."""
        return asyncio.run(self.query_async(query))

# ---- AGENT INTERACTION FUNCTIONS ----

def call_agent(query: str) -> str:
    """Synchronous wrapper for agent interaction."""
    research_agent = DeepResearchAgent()
    return research_agent.query(query)

async def call_agent_async(query: str) -> str:
    """Asynchronous agent interaction."""
    research_agent = DeepResearchAgent()
    return await research_agent.query_async(query)

def get_workflow_config() -> dict:
    """Get the loaded workflow configuration."""
    return workflow_config

if __name__ == "__main__":
    # Example usage
    query = "What are the main initiatives for private equity firms to infuse artificial intelligence into their operations?"
    
    # Print configuration summary
    print(f"Configuration loaded from: {WORKFLOW_CONFIG_PATH}")
    print(f"Model: {MODEL_ID}")
    print(f"RAG MCP Endpoint: {RAG_MCP_ENDPOINT}")
    print(f"Agent: {AGENT_NAME}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    print(f"GOOGLE_API_KEY env var set: {'Yes' if os.environ.get('GOOGLE_API_KEY') else 'No'}")
    print("-" * 50)
    
    try:
        response = call_agent(query)
        print("Agent Response:", response)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()