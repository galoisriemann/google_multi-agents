"""Base agent class for all research agents."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from ..config.config_loader import ConfigLoader
from ..utils.common import get_prompt_template


class BaseResearchAgent(ABC):
    """Base class for research agents.
    
    This class provides common functionality for all research agents,
    including configuration, session management, and basic tool handling.
    """
    
    def __init__(
        self,
        config_path: Union[str, Path],
        prompts_path: Union[str, Path],
        agent_name: str,
        agent_description: str,
        required_config_keys: Optional[List[str]] = None
    ):
        """Initialize the base agent.
        
        Args:
            config_path: Path to the agent's configuration file
            prompts_path: Path to the prompts configuration file
            agent_name: Name of the agent
            agent_description: Description of the agent's purpose
            required_config_keys: List of required configuration keys
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.load_config()
        self.prompts_config = {}
        self.load_prompts(prompts_path)
        
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.required_config_keys = required_config_keys or []
        
        self.runner = None
        self.session = None
        self.initialized = False
    
    def load_prompts(self, prompts_path: Union[str, Path]) -> None:
        """Load prompts configuration.
        
        Args:
            prompts_path: Path to the prompts configuration file
        """
        from ..config.config_loader import load_prompts_config
        self.prompts_config = load_prompts_config(prompts_path)
    
    def get_prompt(self, template_name: str, category: Optional[str] = None) -> str:
        """Get a prompt template by name and optional category.
        
        Args:
            template_name: Name of the template to retrieve
            category: Optional category under which the template is organized
            
        Returns:
            The prompt template string
        """
        return get_prompt_template(self.prompts_config, template_name, category)
    
    def validate_config(self) -> None:
        """Validate that required configuration values are present."""
        if not self.required_config_keys:
            return
            
        missing_keys = self.config_loader.validate_required_keys(self.required_config_keys)
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    async def initialize(self) -> None:
        """Initialize the agent and its dependencies."""
        if self.initialized:
            return
            
        self.validate_config()
        
        # Create agent with basic configuration
        # Note: We're not passing tools here as we'll handle them explicitly
        self.agent = Agent(
            name=self.agent_name,
            model=self.config_loader.get_value("core_config.model"),
            description=self.agent_description,
            instruction=self.get_agent_instruction()
        )
        
        await self._create_session()

        # Setup runner and session
        self.runner = Runner(
            agent=self.agent, 
            app_name=self.config_loader.get_value("app_config.app_name"),
            session_service=self.session
        )
        
        
        self.initialized = True
    
    async def _create_session(self) -> None:
        session_service = InMemorySessionService()

        self.session = session_service.create_session(
            app_name=self.config_loader.get_value("app_config.app_name"),
            user_id=self.config_loader.get_value("app_config.user_id", "default_user"),
            session_id=self.config_loader.get_value("app_config.session_id", "default_session"),
        )
    
    @abstractmethod
    def get_tools(self) -> list:
        """Get the tools available to this agent.
        
        Returns:
            List of tool instances
        """
        pass
    
    @abstractmethod
    def get_agent_instruction(self) -> str:
        """Get the instruction prompt for the agent.
        
        Returns:
            Instruction string
        """
        pass
    
    def get_initial_state(self) -> Dict[str, Any]:
        """Get additional initial state for the session.
        
        Can be overridden by subclasses to add custom state.
        
        Returns:
            Dictionary of additional state values
        """
        return {}
    
    async def query(self, query: str, **kwargs) -> Any:
        """Execute a query with the agent.
        
        Args:
            query: The query to execute
            **kwargs: Additional arguments for the query
            
        Returns:
            The result of the query
        """
        if not self.initialized:
            await self.initialize()
            
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run the agent and process events
        events = self.runner.run_async(
            user_id=self.session.user_id,
            session_id=self.session.id,
            new_message=content,
            **kwargs
        )
        
        return await self.process_events(events)
    
    @abstractmethod
    async def process_events(self, events) -> Any:
        """Process events from the agent's execution.
        
        Args:
            events: Events from the agent's execution
            
        Returns:
            Processed result
        """
        pass
