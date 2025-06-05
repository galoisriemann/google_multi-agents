"""Workflow management module for the Google ADK SDK workflow system.

This module contains the core workflow management logic, including configuration loading,
agent creation, and workflow execution.
"""

import os
import yaml
import logging
import uuid
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from data_model.data_models import (
    WorkflowConfig,
    PromptConfig,
    WorkflowInput,
    WorkflowOutput,
    WorkflowStatus,
    LLMConfig,
    APIConfig,
)
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class WorkflowPaths:
    """Workflow directory paths configuration."""
    base_dir: Path = Path(__file__).parent
    config_dir: Path = None
    prompts_dir: Path = None
    input_dir: Path = None
    output_dir: Path = None
    workflow_config: Path = None
    prompts_config: Path = None
    gemini_config: Path = None

    def __post_init__(self):
        """Initialize derived paths."""
        self.config_dir = self.base_dir / "config"
        self.prompts_dir = self.base_dir / "prompts"
        self.input_dir = self.base_dir / "input"
        self.output_dir = self.base_dir / "output"
        self.workflow_config = self.config_dir / "workflow_config.yml"
        self.prompts_config = self.prompts_dir / "prompts.yml"
        self.gemini_config = self.config_dir / "gemini_config.yml"

    def ensure_directories(self) -> None:
        """Ensure all directories exist."""
        for dir_path in [self.config_dir, self.prompts_dir, self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directories exist: {[str(d) for d in [self.config_dir, self.prompts_dir, self.input_dir, self.output_dir]]}")


class ConfigLoader:
    """Configuration loader for YAML files."""
    
    def __init__(self, paths: WorkflowPaths):
        """Initialize the config loader.
        
        Args:
            paths: WorkflowPaths instance containing file paths.
        """
        self.paths = paths
        
    def load_workflow_config(self) -> WorkflowConfig:
        """Load workflow configuration from YAML file.
        
        Returns:
            WorkflowConfig instance.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            yaml.YAMLError: If YAML parsing fails.
        """
        try:
            logger.debug(f"Loading workflow config from: {self.paths.workflow_config}")
            with open(self.paths.workflow_config, 'r') as f:
                data = yaml.safe_load(f)
            
            config = WorkflowConfig(
                name=data['name'],
                description=data['description'],
                version=data['version'],
                api_config=data['api_config'],
                steps=data.get('steps', []),
                metadata=data.get('metadata', {})
            )
            logger.debug("Workflow config loaded successfully")
            return config
            
        except FileNotFoundError:
            logger.error(f"Workflow config file not found: {self.paths.workflow_config}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing workflow config YAML: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required key in workflow config: {e}")
            raise

    def load_prompts_config(self) -> PromptConfig:
        """Load prompts configuration from YAML file.
        
        Returns:
            PromptConfig instance.
            
        Raises:
            FileNotFoundError: If prompts file doesn't exist.
            yaml.YAMLError: If YAML parsing fails.
        """
        try:
            logger.debug(f"Loading prompts config from: {self.paths.prompts_config}")
            with open(self.paths.prompts_config, 'r') as f:
                data = yaml.safe_load(f)
            
            config = PromptConfig(
                version=data['version'],
                prompts=data['prompts']
            )
            logger.debug("Prompts config loaded successfully")
            return config
            
        except FileNotFoundError:
            logger.error(f"Prompts config file not found: {self.paths.prompts_config}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing prompts config YAML: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required key in prompts config: {e}")
            raise

    def load_llm_config(self) -> Dict[str, Any]:
        """Load LLM configuration from YAML file.
        
        Returns:
            Dictionary containing LLM configuration.
            
        Raises:
            FileNotFoundError: If gemini config file doesn't exist.
            yaml.YAMLError: If YAML parsing fails.
            ValueError: If API key is not found in YAML or environment variables.
        """
        try:
            logger.debug(f"Loading LLM config from: {self.paths.gemini_config}")
            with open(self.paths.gemini_config, 'r') as f:
                data = yaml.safe_load(f)
            
            # Try to get API key from YAML config first, then fallback to environment variable
            api_key = data.get('api_config', {}).get('api_key')
            if not api_key:
                logger.debug("No API key found in YAML config, checking environment variable")
                api_key = os.environ.get('GOOGLE_API_KEY')
                
            if not api_key:
                raise ValueError(
                    "API key not found. Please either:\n"
                    "1. Add api_key to api_config section in gemini_config.yml, OR\n"
                    "2. Set GOOGLE_API_KEY environment variable"
                )
            
            # Set the API key for Google ADK
            logger.debug("Setting GOOGLE_API_KEY for Google ADK")
            os.environ['GOOGLE_API_KEY'] = api_key
            
            # Ensure the API key is in the config data structure
            if 'api_config' not in data:
                data['api_config'] = {}
            data['api_config']['api_key'] = api_key
            
            logger.debug("LLM config loaded successfully and API key set")
            return data
            
        except FileNotFoundError:
            logger.error(f"LLM config file not found: {self.paths.gemini_config}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing LLM config YAML: {e}")
            raise
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise


class AgentFactory:
    """Factory for creating LLM agents with proper configuration."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the agent factory.
        
        Args:
            config_loader: ConfigLoader instance for loading configurations.
        """
        self.config_loader = config_loader
        
    def _create_llm_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create LLM configuration from agent config.
        
        Args:
            config: Agent configuration dictionary.
            
        Returns:
            Dictionary containing LLM configuration.
        """
        try:
            # Get default LLM config
            default_config = self.config_loader.load_llm_config()
            
            # Create API config
            api_config = APIConfig(
                api_key=default_config.get('api_config', {}).get('api_key', ''),
                timeout=default_config.get('api_config', {}).get('timeout', 60)
            )
            
            # Create LLM config
            llm_config = {
                'provider': default_config.get('provider', 'gemini'),
                'model': config.get('model', default_config.get('model', 'gemini-1.5-flash')),
                'temperature': default_config.get('temperature', 0.7),
                'max_tokens': default_config.get('max_tokens', 2048),
                'api_config': api_config,
                'backend': default_config.get('backend', 'google'),
                'step_models': default_config.get('step_models', {})
            }
            
            logger.debug(f"Created LLM config: {llm_config}")
            return llm_config
            
        except Exception as e:
            logger.error(f"Error creating LLM config: {e}")
            raise

    def create_agent(self, config: Dict[str, Any]) -> LlmAgent:
        """Create a single LLM agent with proper configuration.
        
        Args:
            config: Agent configuration dictionary.
            
        Returns:
            LlmAgent instance.
        """
        try:
            # Create LLM configuration
            llm_config = self._create_llm_config(config)
            
            # Get instruction from prompts config using prompt_key
            prompts_config = self.config_loader.load_prompts_config()
            prompt_key = config.get('prompt_key', '')
            instruction = prompts_config.prompts.get(prompt_key, '')
            
            if not instruction:
                raise ValueError(f"No instruction found for prompt_key: {prompt_key}")
            
            # Create LLM agent with the correct parameters for Google ADK
            agent = LlmAgent(
                name=config['name'],
                model=llm_config['model'],
                instruction=instruction
            )
            
            logger.debug(f"Created agent {config['name']} with model: {llm_config['model']}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent {config.get('name', 'unknown')}: {e}")
            raise

    def create_agents(self, agent_configs: List[Dict[str, Any]]) -> List[LlmAgent]:
        """Create multiple LLM agents from configuration.
        
        Args:
            agent_configs: List of agent configuration dictionaries.
            
        Returns:
            List of LlmAgent instances.
        """
        agents = []
        
        for config in agent_configs:
            agent = self.create_agent(config)
            agents.append(agent)
            
        logger.debug(f"Created {len(agents)} agents")
        return agents


class WorkflowManager:
    """Manages workflow execution using Google ADK."""
    
    def __init__(self, config_loader: ConfigLoader):
        """Initialize the workflow manager.
        
        Args:
            config_loader: ConfigLoader instance for loading configurations.
        """
        self.config_loader = config_loader
        self.workflow_config = self.config_loader.load_workflow_config()
        self.prompts_config = self.config_loader.load_prompts_config()
        self.agent_factory = AgentFactory(config_loader)

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data through the workflow.

        Args:
            input_data: Dictionary containing input data with 'prompt' key.

        Returns:
            Dictionary containing workflow results.
        """
        start_time = datetime.now().isoformat()
        session_id = None
        
        try:
            # Validate input data
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            if "prompt" not in input_data:
                raise ValueError("Input data must contain a 'prompt' key")
                
            logger.info(f"Processing input: {input_data}")
            
            # Create agents for the workflow from the steps configuration
            agents = self.agent_factory.create_agents(self.workflow_config.steps)
            
            # Create a sequential agent from the list of agents
            sequential_agent = SequentialAgent(
                name="workflow_sequential_agent",
                sub_agents=agents
            )
            
            # Create the runner with the sequential agent
            app_name = "workflow_app"
            runner = InMemoryRunner(
                agent=sequential_agent,
                app_name=app_name
            )
            
            # Create session using the runner's session service
            # This is the proper ADK pattern for session creation
            # Include the prompt as initial state for context variables
            user_id = "workflow_user"
            user_prompt = input_data["prompt"]
            initial_state = {"prompt": user_prompt}
            
            session = await runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                state=initial_state
            )
            session_id = session.id
            
            # Create content with user input
            content = types.Content(parts=[types.Part(text=user_prompt)])
            
            # Run the workflow
            logger.info(f"Running workflow with session_id: {session_id}")
            response_generator = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            )
            
            # Collect all responses from the async generator
            responses = []
            async for response_item in response_generator:
                responses.append(response_item)
                logger.debug(f"Received response: {response_item}")
            
            # Get the final response
            final_response = responses[-1] if responses else None
            
            # Process the response
            result = {
                "status": WorkflowStatus.COMPLETED,
                "start_time": start_time,
                "end_time": datetime.now().isoformat(),
                "output": {
                    "response": str(final_response),
                    "all_responses": [str(r) for r in responses],
                    "agents_used": [agent.name for agent in agents]
                },
                "session_id": session_id
            }
            
            logger.info("Workflow completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Workflow processing failed: {str(e)}"
            logger.error(error_msg)
            
            return {
                "status": WorkflowStatus.FAILED,
                "start_time": start_time,
                "end_time": datetime.now().isoformat(),
                "error": str(e),
                "session_id": session_id
            } 