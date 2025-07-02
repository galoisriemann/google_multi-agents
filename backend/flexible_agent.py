"""Configurable Flexible Workflow using Google's ADK SDK.

This module implements a flexible workflow system that can handle any number of agents
with configurable types, models, and prompts. Supports:
- LlmAgent: Language model agents with custom instructions
- SequentialAgent: Agents that run sub-agents in sequence
- ParallelAgent: Agents that run sub-agents in parallel
- LoopAgent: Agents that repeat operations until a condition is met
"""

import asyncio
import copy
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

# Add project root to Python path for direct execution
if __name__ == "__main__" and not __package__:
    # Get the project root (parent of backend directory)
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# Try absolute imports first (for module execution), then relative imports (for direct execution)
try:
    from backend.data_model.data_models import WorkflowInput, WorkflowStatus
    from backend.core.config.config_loader import ConfigLoader
    from backend.core.utils.document_reader import DocumentReader, DocumentReaderError
except ImportError:
    # If absolute imports fail, try relative imports for direct execution
    from data_model.data_models import WorkflowInput, WorkflowStatus
    from core.config.config_loader import ConfigLoader
    from core.utils.document_reader import DocumentReader, DocumentReaderError

# Third-party imports
from pydantic import BaseModel, Field, ValidationError

# Google ADK imports
from google.adk.agents import (
    BaseAgent, LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
)
from google.adk.runners import InMemoryRunner
from google.adk.events import Event, EventActions
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('flexible_workflow.log')
    ]
)
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Configuration Models
# ----------------------------------------------------------------------------

class FlexibleAgentConfig(BaseModel):
    """Configuration model for individual flexible agents."""
    name: str
    type: str = Field(..., pattern="^(LlmAgent|SequentialAgent|ParallelAgent|LoopAgent)$")
    model: Optional[str] = None
    description: Optional[str] = None
    instruction: Optional[str] = None
    prompt_key: Optional[str] = None  # Key to load prompt from prompts config
    input_key: Optional[str] = None  # Filename of input document (PDF/DOCX) to inject as context
    tools: List[str] = Field(default_factory=list)
    output_key: Optional[str] = None
    sub_agents: List[str] = Field(default_factory=list)
    max_iterations: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    extra: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""
        extra = "allow"


class FlexibleWorkflowConfig(BaseModel):
    """Configuration model for the entire flexible workflow."""
    name: str
    description: str
    version: str
    main_agent: str  # Name of the main agent to execute
    agents: List[FlexibleAgentConfig]

    class Config:
        """Pydantic config."""
        extra = "allow"


# ----------------------------------------------------------------------------
# Tool Registry
# ----------------------------------------------------------------------------

class FlexibleToolRegistry:
    """Registry for tools that can be used by flexible agents."""
    _tools: Dict[str, Callable] = {}

    @classmethod
    def register(cls, func: Callable) -> Callable:
        """Register a tool function."""
        cls._tools[func.__name__] = func
        return func

    @classmethod
    def get(cls, name: str) -> Callable:
        """Get a registered tool by name."""
        if name in cls._tools:
            return cls._tools[name]
        raise KeyError(f"Tool '{name}' not found in registry.")

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())


# ----------------------------------------------------------------------------
# Example Tools (can be extended)
# ----------------------------------------------------------------------------

@FlexibleToolRegistry.register
def text_processor(text: str) -> str:
    """Example tool: process text."""
    return f"Processed: {text}"

@FlexibleToolRegistry.register
def text_analyzer(text: str) -> str:
    """Example tool: analyze text."""
    return f"Analysis of: {text}"

@FlexibleToolRegistry.register
def code_formatter(code: str) -> str:
    """Example tool: format code."""
    return f"Formatted code:\n{code}"

@FlexibleToolRegistry.register
def data_validator(data: str) -> str:
    """Example tool: validate data."""
    return f"Validated: {data}"


# ----------------------------------------------------------------------------
# Loop Checker Agent for Loop Termination
# ----------------------------------------------------------------------------

class FlexibleLoopChecker(BaseAgent):
    """Agent that checks loop termination conditions for flexible workflows."""
    
    def __init__(self, name: str, stop_keyword: str = "STOP"):
        """Initialize the flexible loop checker.
        
        Args:
            name: Name of the checker agent
            stop_keyword: Keyword to stop the loop when found
        """
        super().__init__(name=name)
        self.stop_keyword = stop_keyword

    async def _run_async_impl(self, context):
        """Check if loop should stop based on last result."""
        last_result = context.session.state.get("last_result", "")
        should_stop = self.stop_keyword.lower() in last_result.lower()
        verdict = "stop" if should_stop else "continue"
        
        actions = EventActions(escalate=should_stop)
        yield Event(
            author=self.name,
            content=types.Content(role="assistant", parts=[types.Part(text=verdict)]),
            actions=actions
        )


# ----------------------------------------------------------------------------
# Agent Factory
# ----------------------------------------------------------------------------

FLEXIBLE_AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {
    "LlmAgent": LlmAgent,
    "SequentialAgent": SequentialAgent,
    "ParallelAgent": ParallelAgent,
    "LoopAgent": LoopAgent,
}


class FlexibleAgentFactory:
    """Factory for creating flexible agents from configuration."""
    
    def __init__(self, configs: List[FlexibleAgentConfig], prompts_loader: ConfigLoader, input_directory: Optional[Path] = None, incremental_dir: Optional[Path] = None):
        """Initialize the flexible agent factory."""
        self.configs = {c.name: c for c in configs}
        self.instances: Dict[str, BaseAgent] = {}
        self.prompts_loader = prompts_loader
        self.document_reader = DocumentReader(input_directory)
        self.incremental_dir = incremental_dir
        self.agent_execution_order = {}
        self.saved_outputs = set()

    def _get_prompt(self, prompt_key: str, agent_config: FlexibleAgentConfig) -> str:
        """Get prompt from prompts configuration file and inject input file content if available."""
        try:
            prompt = self.prompts_loader.get_value(f"prompts.{prompt_key}")
            if not prompt:
                raise ValueError(f"Prompt '{prompt_key}' not found in prompts configuration")
            
            # Inject input file content if specified
            input_content = ""
            if hasattr(agent_config, 'input_key') and agent_config.input_key:
                try:
                    input_content = self.document_reader.read_document(agent_config.input_key)
                    if input_content:
                        logger.info(f"Loaded input document '{agent_config.input_key}' for agent '{agent_config.name}'")
                    else:
                        logger.info(f"No input document found for '{agent_config.input_key}' - using empty content")
                except DocumentReaderError as e:
                    logger.warning(f"Failed to read input document '{agent_config.input_key}': {e}")
                    input_content = ""
            
            # Inject input content into prompt if available
            if input_content:
                prompt = f"{prompt}\n\n**Additional Input Document:**\n{input_content}"
            
            return prompt
        except Exception as e:
            logger.error(f"Failed to load prompt '{prompt_key}': {e}")
            raise

    def _create_after_model_callback(self, agent_name: str):
        """Create an after_model callback for saving individual agent outputs.
        
        Uses after_model_callback (not after_agent_callback) to get immediate access
        to the LLM response as soon as the model returns, enabling real-time saving
        of individual agent outputs during workflow execution.
        
        Args:
            agent_name: Name of the agent to create callback for
            
        Returns:
            Callback function that accepts (callback_context, llm_response) parameters
            and returns None to pass through the original response unchanged.
        """
        def after_model_callback(callback_context, llm_response):
            """Callback to save agent output immediately after model responds."""
            try:
                if not self.incremental_dir or agent_name in self.saved_outputs:
                    return None  # Don't modify response, just pass through
                
                # Get execution order
                if agent_name not in self.agent_execution_order:
                    self.agent_execution_order[agent_name] = len(self.agent_execution_order) + 1
                
                execution_order = self.agent_execution_order[agent_name]
                
                # Extract content from LLM response
                content = ""
                
                if llm_response and llm_response.content and llm_response.content.parts:
                    for part in llm_response.content.parts:
                        if hasattr(part, 'text') and part.text:
                            content += part.text
                        elif hasattr(part, 'function_call'):
                            # For function calls, we'll save a description
                            func_call = part.function_call
                            content += f"Function Call: {func_call.name}\nArguments: {func_call.args}\n"
                elif llm_response and hasattr(llm_response, 'error_message') and llm_response.error_message:
                    content = f"Error: {llm_response.error_message}"
                
                if content and len(content.strip()) > 0:
                    # Save immediately using sync method in callback
                    self._save_agent_output_sync(agent_name, content, execution_order)
                    self.saved_outputs.add(agent_name)
                    logger.info(f"🔄 Model callback saved output for agent: {agent_name} ({len(content)} chars)")
                else:
                    logger.warning(f"⚠️ No content found in model callback for agent: {agent_name}")
                
                # Return None to pass through original response unchanged
                return None
                
            except Exception as e:
                logger.error(f"Error in after_model_callback for {agent_name}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return None  # Don't modify response on error
        
        return after_model_callback
    
    def _save_agent_output_sync(self, agent_name: str, content: str, execution_order: int):
        """Synchronous method to save agent output from callback."""
        try:
            if not self.incremental_dir:
                return
                
            filename = f"{execution_order:02d}_{agent_name.lower().replace(' ', '_')}.md"
            file_path = self.incremental_dir / filename
            
            # Create markdown content
            from datetime import datetime
            markdown_content = f"""# {agent_name} Output
**Agent**: {agent_name}
**Execution Order**: {execution_order}
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{content}

---
*Saved by after_agent_callback on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"💾 Saved agent output: {filename} ({len(content)} chars)")
            
        except Exception as e:
            logger.error(f"Failed to save output for {agent_name}: {e}")
    
    def _get_agent_config_by_name(self, agent_name: str):
        """Get agent configuration by name."""
        try:
            for config in self.configs.values():
                if config.name == agent_name:
                    return config
            return None
        except Exception as e:
            logger.error(f"Error getting agent config for {agent_name}: {e}")
            return None

    def build_all(self) -> Dict[str, BaseAgent]:
        """Build all flexible agents from configurations."""
        # First pass: instantiate each agent
        for cfg in self.configs.values():
            try:
                agent = self._create_agent(cfg)
                setattr(agent, '_pending_subs', cfg.sub_agents)
                self.instances[cfg.name] = agent
                logger.info(f"Created flexible agent: {cfg.name} ({cfg.type})")
            except Exception as e:
                logger.error(f"Failed to create flexible agent {cfg.name}: {e}")
                raise

        # Second pass: wire sub_agents
        for agent in self.instances.values():
            pending = getattr(agent, '_pending_subs', [])
            if pending:
                sub_agents = []
                for sub_name in pending:
                    if sub_name in self.instances:
                        sub_agents.append(self.instances[sub_name])
                    else:
                        logger.warning(f"Sub-agent '{sub_name}' not found for agent '{agent.name}'")
                agent.sub_agents = sub_agents
            
            # Clean up temporary attribute
            if hasattr(agent, '_pending_subs'):
                delattr(agent, '_pending_subs')

        return self.instances

    def _create_agent(self, cfg: FlexibleAgentConfig) -> BaseAgent:
        """Create a single flexible agent from configuration."""
        try:
            logger.info(f"🔧 Creating agent: {cfg.name} (type: {cfg.type})")
            
            cls = FLEXIBLE_AGENT_CLASSES[cfg.type]
            kwargs: Dict[str, Any] = {"name": cfg.name}
            
            # Add common attributes
            if cfg.description:
                kwargs["description"] = cfg.description
                logger.debug(f"   Added description: {cfg.description}")
            
            # LlmAgent specific attributes
            if cfg.type == "LlmAgent":
                if cfg.model:
                    kwargs["model"] = cfg.model
                    logger.debug(f"   Added model: {cfg.model}")
                
                # Get instruction from prompt_key or direct instruction
                if cfg.prompt_key:
                    kwargs["instruction"] = self._get_prompt(cfg.prompt_key, cfg)
                    logger.debug(f"   Added instruction from prompt_key: {cfg.prompt_key}")
                elif cfg.instruction:
                    kwargs["instruction"] = cfg.instruction
                    logger.debug(f"   Added direct instruction")
                
                if cfg.output_key:
                    kwargs["output_key"] = cfg.output_key
                    logger.debug(f"   Added output_key: {cfg.output_key}")
                
                # Add after_model callback for individual file saving
                if self.incremental_dir:
                    kwargs["after_model_callback"] = self._create_after_model_callback(cfg.name)
                    logger.debug(f"   Added after_model_callback for incremental saving")
            
            # Add tools if specified
            if cfg.tools:
                try:
                    kwargs["tools"] = [FlexibleToolRegistry.get(name) for name in cfg.tools]
                    logger.debug(f"   Added tools: {cfg.tools}")
                except KeyError as e:
                    logger.warning(f"Tool not found for flexible agent {cfg.name}: {e}")
            
            # LoopAgent specific attributes
            if cfg.type == "LoopAgent" and cfg.max_iterations is not None:
                logger.debug(f"   Adding max_iterations: {cfg.max_iterations} (type: {type(cfg.max_iterations)})")
                if isinstance(cfg.max_iterations, dict):
                    logger.error(f"❌ max_iterations is a dict but should be int: {cfg.max_iterations}")
                    raise ValueError(f"max_iterations must be an integer, got dict: {cfg.max_iterations}")
                kwargs["max_iterations"] = cfg.max_iterations
            
            # Note: LlmAgent doesn't accept temperature, max_tokens etc. directly
            # These would need to be configured at the model/API level
            # Only add extra parameters that are actually supported by the agent class
            supported_params = {"name", "model", "instruction", "description", "output_key", "tools", "sub_agents", "max_iterations"}
            
            # Filter extra parameters to only include supported ones
            for key, value in cfg.extra.items():
                if key in supported_params:
                    logger.debug(f"   Adding extra param {key}: {value} (type: {type(value)})")
                    if key == "max_iterations" and isinstance(value, dict):
                        logger.error(f"❌ Extra param {key} is a dict but should be int: {value}")
                        raise ValueError(f"Parameter {key} must be an integer, got dict: {value}")
                    kwargs[key] = value
                else:
                    logger.debug(f"   Skipping unsupported param: {key} = {value}")
                    
            # Skip unsupported parameters like temperature, max_tokens
            # These would be handled at the API/model level, not the agent level
            
            logger.info(f"   Creating {cfg.type} with kwargs: {list(kwargs.keys())}")
            
            # Log the actual kwargs values for debugging
            for k, v in kwargs.items():
                logger.debug(f"     {k}: {type(v)} = {v}")
            
            agent = cls(**kwargs)
            logger.info(f"✅ Successfully created agent: {cfg.name}")
            return agent
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent {cfg.name}: {e}")
            logger.error(f"   Agent config: {cfg}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            raise


# ----------------------------------------------------------------------------
# Flexible Workflow Manager
# ----------------------------------------------------------------------------

class FlexibleWorkflowManager:
    """Manages flexible workflows with multiple agent types and configurations."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the flexible workflow manager."""
        self.base_dir = Path(__file__).parent
        self.config_dir = config_dir or (self.base_dir / "config" / "flexible_agent")
        
        # Load configuration files
        self._load_configurations()
        
        # Set up API key
        self._load_api_key()
        
        # Initialize workflow components
        self.main_agent = None
        self.all_agents = {}
        self.runner = None
        self.session = None
        
    def _load_configurations(self) -> None:
        """Load all configuration files."""
        try:
            # Main workflow configuration
            workflow_config_path = self.config_dir / "workflow_flexible.yml"
            self.config_loader = ConfigLoader(workflow_config_path)
            
            # Gemini configuration
            gemini_config_path = self.config_dir / "gemini_config_flexible.yml"
            self.gemini_config_loader = ConfigLoader(gemini_config_path)
            
            # Prompts configuration
            prompts_config_path = self.base_dir / "prompts" / "flexible_agent" / "prompts_flexible.yml"
            self.prompts_loader = ConfigLoader(prompts_config_path)
            
            # Load configurations
            self.config = self.config_loader.load_config()
            self.gemini_config = self.gemini_config_loader.load_config()
            self.prompts_config = self.prompts_loader.load_config()
            
            logger.info("✅ All flexible agent configuration files loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load flexible agent configurations: {e}")
            raise
    
    def _load_api_key(self) -> None:
        """Load the API key from gemini config file."""
        try:
            api_key = self.gemini_config_loader.get_value("api_config.api_key")
            if api_key:
                os.environ['GOOGLE_API_KEY'] = api_key
                logger.info("✅ Google API key loaded successfully for flexible agent")
            else:
                logger.warning("⚠️ No API key found in flexible agent gemini config")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load API key for flexible agent: {e}")
    
    def _parse_workflow_config(self) -> FlexibleWorkflowConfig:
        """Parse workflow configuration into FlexibleWorkflowConfig model."""
        try:
            # Convert steps to agents format for compatibility
            workflow_data = {
                "name": self.config_loader.get_value("name", "Flexible Workflow"),
                "description": self.config_loader.get_value("description", "A flexible multi-agent workflow"),
                "version": self.config_loader.get_value("version", "1.0.0"),
                "main_agent": "MainFlexibleOrchestrator",
                "agents": []
            }
            
            # Get steps from config and convert to agents
            steps = self.config_loader.get_value("steps", [])
            if steps:
                # Create individual LlmAgents from steps
                agent_configs = []
                agent_names = []
                
                for step in steps:
                    agent_config = {
                        "name": step.get("name", f"FlexibleAgent_{len(agent_configs)}"),
                        "type": "LlmAgent",
                        "model": step.get("model", self.config_loader.get_value("core_config.model", "gemini-1.5-flash")),
                        "description": step.get("description", ""),
                        "prompt_key": step.get("prompt_key"),
                        "output_key": step.get("output_key"),
                        "parameters": step.get("parameters", {})
                    }
                    agent_configs.append(agent_config)
                    agent_names.append(agent_config["name"])
                
                # Create main sequential agent that orchestrates all sub-agents
                main_agent_config = {
                    "name": "MainFlexibleOrchestrator",
                    "type": "SequentialAgent",
                    "description": "Main flexible agent that orchestrates the workflow",
                    "sub_agents": agent_names
                }
                
                workflow_data["agents"] = agent_configs + [main_agent_config]
            
            # If no steps, try to load agents directly (new format)
            elif "agents" in self.config:
                workflow_data["agents"] = self.config["agents"]
                workflow_data["main_agent"] = self.config.get("main_agent", "MainFlexibleOrchestrator")
            
            return FlexibleWorkflowConfig(**workflow_data)
            
        except ValidationError as e:
            logger.error(f"Flexible workflow configuration validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse flexible workflow configuration: {e}")
            raise

    async def initialize(self) -> None:
        """Initialize the flexible workflow."""
        logger.info("🔧 Initializing Flexible Workflow")
        
        try:
            # Parse workflow configuration
            workflow_config = self._parse_workflow_config()
            logger.info(f"Flexible Workflow: {workflow_config.name} v{workflow_config.version}")
            
            # Create agent factory and build all agents
            input_directory = self.base_dir / "input"
            factory = FlexibleAgentFactory(workflow_config.agents, self.prompts_loader, input_directory)
            self.all_agents = factory.build_all()
            
            # Get the main agent
            if workflow_config.main_agent not in self.all_agents:
                raise ValueError(f"Main flexible agent '{workflow_config.main_agent}' not found in agents")
            
            self.main_agent = self.all_agents[workflow_config.main_agent]
            logger.info(f"Main flexible agent: {self.main_agent.name} ({type(self.main_agent).__name__})")
            
            # Create runner and session
            app_name = self.config_loader.get_value("app_config.app_name", "flexible_workflow")
            self.runner = InMemoryRunner(
                agent=self.main_agent,
                app_name=app_name
            )
            
            # Create session
            user_id = self.config_loader.get_value("app_config.user_id", "flexible_user")
            session_id = self.config_loader.get_value("app_config.session_id", "flexible_session")
            
            self.session = await self.runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            logger.info(f"✅ Flexible Workflow initialized with {len(self.all_agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize flexible workflow: {e}")
            raise

    async def run_workflow(self, user_request: str) -> Dict[str, Any]:
        """Run the flexible workflow."""
        start_time = datetime.now()
        logger.info(f"🚀 Starting flexible workflow for request: {user_request}")
        
        # Setup incremental saving
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config_loader.get_value("app_config.output_dir", "backend/output"))
        incremental_dir = output_dir / f"incremental_{timestamp}"
        incremental_dir.mkdir(parents=True, exist_ok=True)
        
        # Rebuild agents with callback support for incremental saving
        workflow_config = self._parse_workflow_config()
        input_directory = self.base_dir / "input"
        factory = FlexibleAgentFactory(workflow_config.agents, self.prompts_loader, input_directory, incremental_dir)
        self.all_agents = factory.build_all()
        
        # Update main agent and runner with callback-enabled agents
        if workflow_config.main_agent not in self.all_agents:
            raise ValueError(f"Main flexible agent '{workflow_config.main_agent}' not found in agents")
        
        self.main_agent = self.all_agents[workflow_config.main_agent]
        
        # Recreate runner with callback-enabled agents
        app_name = self.config_loader.get_value("app_config.app_name", "flexible_workflow")
        self.runner = InMemoryRunner(
            agent=self.main_agent,
            app_name=app_name
        )
        
        # Create new session for the new runner
        user_id = self.config_loader.get_value("app_config.user_id", "flexible_user")
        session_id = f"flexible_session_{timestamp}"
        
        self.session = await self.runner.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Save initial workflow metadata
        await self._save_workflow_metadata(incremental_dir, user_request, start_time)
        
        # Track agent execution for better error reporting
        current_agent = None
        executed_agents = []
        agent_outputs = {}  # Store outputs for incremental saving
        
        try:
            # Initialize if not already done
            if not self.main_agent:
                await self.initialize()
            
            # Log all agent configurations for debugging
            self._log_agent_configurations()
            
            # Create user message
            content = types.Content(role='user', parts=[types.Part(text=user_request)])
            
            # Execute the workflow
            # Note: Individual agent outputs are now saved automatically via after_agent_callback
            response_text = ""
            final_state = {}

            async for event in self.runner.run_async(
                user_id=self.session.user_id,
                session_id=self.session.id,
                new_message=content
            ):
                # Track which agent is currently executing
                if hasattr(event, 'agent_name') and event.agent_name:
                    current_agent = event.agent_name
                    if current_agent not in executed_agents:
                        executed_agents.append(current_agent)
                        logger.info(f"🤖 Executing agent: {current_agent} (#{len(executed_agents)})")
                
                # Extract final response
                if event.is_final_response() and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
                
                # Extract state information for final summary
                if hasattr(event, 'state') and event.state:
                    final_state.update(event.state)
            
            # Get the final state from the session
            if not final_state and self.session:
                final_state = getattr(self.session, 'state', {})
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": WorkflowStatus.COMPLETED,
                "content": response_text or "Flexible workflow completed successfully",
                "metadata": {
                    "success": bool(response_text),
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "original_request": user_request,
                    "workflow_type": "flexible",
                    "workflow_name": self.config_loader.get_value("name", "Flexible Workflow"),
                    "workflow_version": self.config_loader.get_value("version", "1.0.0"),
                    "agents_executed": executed_agents,
                    "main_agent": self.main_agent.name,
                    "total_agents": len(self.all_agents),
                    "model_used": self.config_loader.get_value("core_config.model", "gemini-1.5-flash"),
                    "incremental_output_dir": str(incremental_dir)
                },
                "state": final_state
            }
            
            # Save final comprehensive results
            await self._save_results(result)
            
            # Get outputs saved by callbacks
            callback_outputs = {}
            if hasattr(factory, 'saved_outputs'):
                callback_outputs = {name: "Saved via callback" for name in factory.saved_outputs}
            
            # Save final summary to incremental directory
            await self._save_final_summary(incremental_dir, result, executed_agents, callback_outputs)
            
            logger.info(f"✅ Flexible workflow completed successfully in {execution_time:.2f}s")
            logger.info(f"📁 Incremental outputs saved to: {incremental_dir}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Enhanced error reporting with agent and model details
            error_details = self._analyze_error(e, current_agent, executed_agents)
            error_msg = f"Flexible workflow failed: {str(e)}"
            
            # Log detailed error information
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Failed Agent: {error_details['failed_agent']}")
            logger.error(f"   Agent Model: {error_details['agent_model']}")
            logger.error(f"   Agent Type: {error_details['agent_type']}")
            logger.error(f"   Executed Agents: {executed_agents}")
            logger.error(f"   Error Type: {error_details['error_type']}")
            
            # Get outputs saved by callbacks for error report
            callback_outputs = {}
            if 'factory' in locals() and hasattr(factory, 'saved_outputs'):
                callback_outputs = {name: "Saved via callback" for name in factory.saved_outputs}
            
            # Save error details to incremental directory
            await self._save_error_details(incremental_dir, error_details, executed_agents, callback_outputs)
            
            result = {
                "status": WorkflowStatus.FAILED,
                "content": error_msg,
                "metadata": {
                    "success": False,
                    "execution_time": execution_time,
                    "timestamp": start_time.isoformat(),
                    "error": str(e),
                    "error_details": error_details,
                    "executed_agents": executed_agents,
                    "workflow_type": "flexible",
                    "workflow_name": self.config_loader.get_value("name", "Flexible Workflow"),
                    "workflow_version": self.config_loader.get_value("version", "1.0.0"),
                    "incremental_output_dir": str(incremental_dir)
                }
            }
            
            logger.info(f"📁 Partial outputs saved to: {incremental_dir}")
            return result

    async def _save_workflow_metadata(self, incremental_dir: Path, user_request: str, start_time: datetime) -> None:
        """Save initial workflow metadata and configuration."""
        try:
            metadata_file = incremental_dir / "00_workflow_metadata.md"
            
            metadata_content = f"""# Flexible Workflow Execution - Metadata

## 🚀 Workflow Information
- **Workflow Name**: {self.config_loader.get_value('name', 'Flexible Workflow')}
- **Version**: {self.config_loader.get_value('version', '1.0.0')}
- **Started**: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **Type**: Flexible Multi-Agent Workflow

## 📝 Original Request
```
{user_request}
```

## 🤖 Agent Configuration
- **Main Agent**: {self.config_loader.get_value('main_agent', 'MainFlexibleOrchestrator')}
- **Model**: {self.config_loader.get_value('core_config.model', 'gemini-1.5-flash')}
- **Total Agents**: {len(self.all_agents) if self.all_agents else 0}

### Available Agents:
"""
            
            if self.all_agents:
                for i, (name, agent) in enumerate(self.all_agents.items(), 1):
                    agent_type = type(agent).__name__
                    metadata_content += f"{i}. **{name}** ({agent_type})\n"
            
            metadata_content += f"""
## 📁 Output Organization
- This directory contains incremental outputs from each agent
- Files are numbered in execution order
- Each agent's output is saved immediately upon completion
- If the workflow fails, you'll have outputs up to the failure point

---
*Generated by FlexibleWorkflowManager on {start_time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write(metadata_content)
                
            logger.info(f"📋 Workflow metadata saved: {metadata_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save workflow metadata: {e}")

    async def _save_agent_output_incremental(
        self, 
        incremental_dir: Path, 
        agent_name: str, 
        output: str, 
        execution_order: int,
        agent_outputs: Dict[str, str]
    ) -> None:
        """Save individual agent output immediately as markdown file."""
        try:
            if not output or not isinstance(output, str) or len(output.strip()) == 0:
                return
            
            # Avoid duplicate saves
            if agent_name in agent_outputs:
                return
                
            agent_outputs[agent_name] = output
            
            # Create filename with execution order for proper sorting
            safe_agent_name = agent_name.lower().replace(' ', '_').replace('-', '_')
            output_file = incremental_dir / f"{execution_order:02d}_{safe_agent_name}.md"
            
            # Get agent configuration for context
            agent_config = self._get_agent_config_for_output(agent_name)
            
            # Format output as markdown
            formatted_output = f"""# {agent_name.replace('_', ' ').title()} Output

## 🤖 Agent Information
- **Agent Name**: {agent_name}
- **Agent Type**: {agent_config.get('type', 'Unknown')}
- **Model**: {agent_config.get('model', 'Unknown')}
- **Execution Order**: {execution_order}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Output Key
**Output Key**: `{agent_config.get('output_key', agent_name)}`

## 📝 Generated Output

{output}

---
*Generated by {agent_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_output)
            
            logger.info(f"💾 Agent output saved: {output_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save agent output for {agent_name}: {e}")

    def _get_agent_config_for_output(self, agent_name: str) -> Dict[str, Any]:
        """Get agent configuration for output context."""
        try:
            agents_config = self.config_loader.get_value('agents', [])
            for agent_config in agents_config:
                if agent_config.get('name') == agent_name:
                    return agent_config
            return {"type": "Unknown", "model": "Unknown", "output_key": agent_name}
        except:
            return {"type": "Unknown", "model": "Unknown", "output_key": agent_name}

    async def _save_final_summary(
        self, 
        incremental_dir: Path, 
        result: Dict[str, Any], 
        executed_agents: List[str],
        agent_outputs: Dict[str, str]
    ) -> None:
        """Save final workflow summary to incremental directory."""
        try:
            summary_file = incremental_dir / "99_final_summary.md"
            metadata = result.get("metadata", {})
            
            summary_content = f"""# Workflow Execution Summary

## ✅ Final Status: {result.get('status', 'Unknown')}

## 📊 Execution Metrics
- **Success**: {metadata.get('success', False)}
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Total Agents**: {metadata.get('total_agents', 0)}
- **Agents Executed**: {len(executed_agents)}
- **Agents with Outputs**: {len(agent_outputs)}

## 🤖 Agent Execution Order
"""
            
            for i, agent in enumerate(executed_agents, 1):
                status = "✅ Completed" if agent in agent_outputs else "⏸️ No Output"
                summary_content += f"{i}. **{agent}** - {status}\n"
            
            summary_content += f"""
## 📝 Final Response
{result.get('content', 'No final response available')}

## 📁 Generated Files
"""
            
            # List all generated files
            try:
                for file_path in sorted(incremental_dir.glob("*.md")):
                    if file_path.name != "99_final_summary.md":
                        summary_content += f"- `{file_path.name}`\n"
            except:
                summary_content += "- Error listing generated files\n"
            
            summary_content += f"""
## 🎯 Workflow Performance
- **Average time per agent**: {metadata.get('execution_time', 0) / max(len(executed_agents), 1):.2f}s
- **Success rate**: {len(agent_outputs) / max(len(executed_agents), 1) * 100:.1f}%

---
*Workflow completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"📋 Final summary saved: {summary_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save final summary: {e}")

    async def _save_error_details(
        self, 
        incremental_dir: Path, 
        error_details: Dict[str, Any],
        executed_agents: List[str],
        agent_outputs: Dict[str, str]
    ) -> None:
        """Save error details and partial results when workflow fails."""
        try:
            error_file = incremental_dir / "99_error_report.md"
            
            error_content = f"""# ❌ Workflow Execution Failed

## 🚨 Error Details
- **Failed Agent**: {error_details.get('failed_agent', 'Unknown')}
- **Agent Type**: {error_details.get('agent_type', 'Unknown')}
- **Agent Model**: {error_details.get('agent_model', 'Unknown')}
- **Error Type**: {error_details.get('error_type', 'Unknown')}
- **Error Category**: {error_details.get('error_category', 'Unknown')}
- **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📝 Error Message
```
{error_details.get('error_message', 'No error message available')}
```

## ✅ Successfully Completed Agents
"""
            
            for i, agent in enumerate(executed_agents, 1):
                status = "✅ Completed with Output" if agent in agent_outputs else "⏸️ Executed (No Output)"
                error_content += f"{i}. **{agent}** - {status}\n"
            
            error_content += f"""
## 📊 Partial Execution Statistics
- **Total Agents in Workflow**: {error_details.get('total_agents_in_workflow', 0)}
- **Agents Executed**: {len(executed_agents)}
- **Agents with Outputs**: {len(agent_outputs)}
- **Success Rate**: {len(agent_outputs) / max(len(executed_agents), 1) * 100:.1f}%

## 💾 Available Outputs
You have the following partial results available:
"""
            
            # List available outputs
            for agent in executed_agents:
                if agent in agent_outputs:
                    safe_name = agent.lower().replace(' ', '_').replace('-', '_')
                    file_pattern = f"*_{safe_name}.md"
                    error_content += f"- **{agent}**: See `{file_pattern}`\n"
            
            error_content += f"""
## 🔧 Troubleshooting
- Check the failed agent configuration
- Verify API quotas and connectivity
- Review agent-specific logs above
- Consider running from the last successful checkpoint

## 🔄 Recovery Options
1. **Partial Results**: Use the outputs from successful agents
2. **Restart from Checkpoint**: Modify workflow to start from last successful agent
3. **Debug Mode**: Run individual agents to isolate the issue

---
*Error report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_content)
            
            logger.info(f"🚨 Error report saved: {error_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save error details: {e}")

    async def _save_results(self, result: Dict[str, Any]) -> None:
        """Save flexible workflow results to output directory in multiple formats."""
        try:
            output_dir = Path(self.config_loader.get_value("app_config.output_dir", "backend/output"))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON result
            result_file = output_dir / f"flexible_workflow_result_{timestamp}.json"
            import json
            result_copy = result.copy()
            if 'status' in result_copy:
                result_copy['status'] = str(result_copy['status'])
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Flexible workflow results saved to: {result_file}")
            
            # Save comprehensive markdown report
            await self._save_markdown_report(result, output_dir, timestamp)
            
            # Save individual agent outputs if available in state (legacy support)
            await self._save_individual_outputs(result, output_dir, timestamp)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save flexible workflow results: {e}")

    async def _save_markdown_report(self, result: Dict[str, Any], output_dir: Path, timestamp: str) -> None:
        """Save a comprehensive markdown report of the workflow execution."""
        try:
            markdown_file = output_dir / f"flexible_workflow_report_{timestamp}.md"
            metadata = result.get("metadata", {})
            state = result.get("state", {})
            
            markdown_content = f"""# Flexible Workflow Execution Report

## 📋 Summary
- **Workflow**: {metadata.get('workflow_name', 'N/A')} v{metadata.get('workflow_version', 'N/A')}
- **Status**: {result.get('status', 'N/A')}
- **Success**: {metadata.get('success', False)}
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Timestamp**: {metadata.get('timestamp', 'N/A')}
- **Workflow Type**: {metadata.get('workflow_type', 'N/A')}
- **Incremental Outputs**: {metadata.get('incremental_output_dir', 'N/A')}

## 🎯 Original Request
```
{metadata.get('original_request', 'N/A')}
```

## 🤖 Agent Configuration
- **Main Agent**: {metadata.get('main_agent', 'N/A')}
- **Total Agents**: {metadata.get('total_agents', 0)}
- **Model Used**: {metadata.get('model_used', 'N/A')}

### Agents Executed:
"""
            
            # Add list of agents
            agents_executed = metadata.get('agents_executed', [])
            for i, agent in enumerate(agents_executed, 1):
                markdown_content += f"{i}. **{agent}**\n"
            
            markdown_content += f"""
## 📝 Final Response
{result.get('content', 'No response content available')}
"""
            
            # Add incremental outputs information
            incremental_dir = metadata.get('incremental_output_dir')
            if incremental_dir:
                markdown_content += f"""
## 📁 Incremental Outputs
Individual agent outputs have been saved to: `{incremental_dir}`

Each agent's output is saved as a separate markdown file with execution order:
- `00_workflow_metadata.md` - Initial workflow configuration
- `01_[agent_name].md` - First agent output
- `02_[agent_name].md` - Second agent output
- `...` - Additional agent outputs in execution order
- `99_final_summary.md` - Execution summary

Note: Actual filenames will match the executed agents in your workflow.
"""
            
            # Add individual agent outputs if available
            if state:
                markdown_content += "\n## 🔍 Individual Agent Outputs\n"
                
                for key, value in state.items():
                    if value and isinstance(value, str):
                        # Format the key to be more readable
                        formatted_key = key.replace('_', ' ').title()
                        markdown_content += f"""
### {formatted_key}
```
{value}
```
"""
            
            # Add performance and metadata section
            markdown_content += f"""
## 📊 Performance Metrics
- **Execution Time**: {metadata.get('execution_time', 0):.2f} seconds
- **Success Rate**: {'100%' if metadata.get('success') else '0%'}
- **Memory Usage**: Available in full JSON report
- **API Calls**: Tracked in session state

## 🔧 Technical Details
- **Workflow Manager**: FlexibleWorkflowManager
- **Runner Type**: InMemoryRunner
- **Session ID**: {self.config_loader.get_value('app_config.session_id', 'N/A')}
- **User ID**: {self.config_loader.get_value('app_config.user_id', 'N/A')}
- **App Name**: {self.config_loader.get_value('app_config.app_name', 'N/A')}
"""
            
            # Add error information if failed
            if not metadata.get('success', True):
                error_msg = metadata.get('error', 'Unknown error')
                markdown_content += f"""
## ❌ Error Information
```
{error_msg}
```
"""
            
            # Add footer
            markdown_content += f"""
---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Flexible Workflow System*
"""
            
            # Write the markdown file
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"📄 Markdown report saved to: {markdown_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save markdown report: {e}")

    async def _save_individual_outputs(self, result: Dict[str, Any], output_dir: Path, timestamp: str) -> None:
        """Save individual agent outputs as separate files if available (legacy support)."""
        try:
            state = result.get("state", {})
            if not state:
                return
            
            # Save each output in state as a separate file
            for key, value in state.items():
                if value and isinstance(value, str) and len(value.strip()) > 0:
                    # Determine file extension based on content
                    if any(keyword in key.lower() for keyword in ['code', 'script', 'program']):
                        if 'python' in value.lower() or 'def ' in value or 'import ' in value:
                            ext = 'py'
                        elif 'javascript' in value.lower() or 'function ' in value or 'const ' in value:
                            ext = 'js'
                        elif 'typescript' in value.lower() or 'interface ' in value:
                            ext = 'ts'
                        else:
                            ext = 'txt'
                    elif any(keyword in key.lower() for keyword in ['review', 'comment', 'analysis', 'report']):
                        ext = 'md'
                    elif any(keyword in key.lower() for keyword in ['config', 'setting']):
                        ext = 'yml'
                    else:
                        ext = 'txt'
                    
                    # Create filename
                    safe_key = key.lower().replace(' ', '_').replace('-', '_')
                    output_file = output_dir / f"{safe_key}_{timestamp}.{ext}"
                    
                    # Write the file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        if ext == 'md' and not value.startswith('#'):
                            # Add markdown header if it's a markdown file without one
                            f.write(f"# {key.replace('_', ' ').title()}\n\n{value}")
                        else:
                            f.write(value)
                    
                    logger.info(f"📁 Individual output saved: {output_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save individual outputs: {e}")

    def _log_agent_configurations(self) -> None:
        """Log detailed agent configurations for debugging."""
        logger.info("🔍 Agent Configuration Details:")
        
        if not self.all_agents:
            logger.warning("   No agents initialized yet")
            return
            
        for agent_name, agent in self.all_agents.items():
            agent_type = type(agent).__name__
            
            # Try to get model from agent or config
            model = "unknown"
            if hasattr(agent, 'model'):
                model = agent.model
            else:
                # Look up in workflow config
                agents_config = self.config_loader.get_value('agents', [])
                for agent_config in agents_config:
                    if agent_config.get('name') == agent_name:
                        model = agent_config.get('model', 'not specified')
                        break
            
            logger.info(f"   📱 {agent_name}: {agent_type} (model: {model})")
    
    def _analyze_error(self, error: Exception, current_agent: str, executed_agents: list) -> Dict[str, Any]:
        """Analyze error and provide detailed information about the failure."""
        error_str = str(error)
        error_type = type(error).__name__
        
        # Determine which agent likely failed
        failed_agent = current_agent or (executed_agents[-1] if executed_agents else "unknown")
        
        # Try to determine the model for the failed agent
        agent_model = "unknown"
        agent_type = "unknown"
        
        if failed_agent and failed_agent in self.all_agents:
            agent = self.all_agents[failed_agent]
            agent_type = type(agent).__name__
            
            # Try to get model from agent
            if hasattr(agent, 'model'):
                agent_model = agent.model
            else:
                # Look up in workflow config
                agents_config = self.config_loader.get_value('agents', [])
                for agent_config in agents_config:
                    if agent_config.get('name') == failed_agent:
                        agent_model = agent_config.get('model', 'not specified')
                        break
        
        # Classify error type
        error_category = "unknown"
        if "503" in error_str and ("overloaded" in error_str.lower() or "unavailable" in error_str.lower()):
            error_category = "api_overloaded"
        elif "429" in error_str:
            error_category = "rate_limit"
        elif "401" in error_str or "unauthorized" in error_str.lower():
            error_category = "authentication"
        elif "400" in error_str:
            error_category = "bad_request"
        elif "timeout" in error_str.lower():
            error_category = "timeout"
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            error_category = "network"
        
        return {
            "failed_agent": failed_agent,
            "agent_model": agent_model,
            "agent_type": agent_type,
            "error_type": error_type,
            "error_category": error_category,
            "error_message": error_str,
            "all_executed_agents": executed_agents,
            "total_agents_in_workflow": len(self.all_agents) if self.all_agents else 0
        }

    def print_configuration_summary(self) -> None:
        """Print a summary of the loaded flexible workflow configuration."""
        logger.info("📋 Flexible Workflow Configuration Summary:")
        logger.info(f"   Workflow Name: {self.config_loader.get_value('name', 'N/A')}")
        logger.info(f"   Workflow Version: {self.config_loader.get_value('version', 'N/A')}")
        logger.info(f"   Model: {self.config_loader.get_value('core_config.model', 'N/A')}")
        logger.info(f"   Available Tools: {FlexibleToolRegistry.list_tools()}")
        if self.all_agents:
            logger.info(f"   Total Agents: {len(self.all_agents)}")
            for name, agent in self.all_agents.items():
                logger.info(f"     - {name}: {type(agent).__name__}")


async def main() -> None:
    """Main entry point for the flexible workflow system."""
    logger.info("🎯 Starting Flexible Workflow System")
    
    try:
        # Create workflow manager
        workflow_manager = FlexibleWorkflowManager()
        
        # Print configuration summary for debugging
        workflow_manager.print_configuration_summary()
        
        # Get example request
        user_request = "Create a comprehensive LLM guided Gartner style market research report generating framework"
        
        # Run the workflow
        result = await workflow_manager.run_workflow(user_request)
        
        # Display results
        print("\n" + "="*80)
        print("🎉 FLEXIBLE WORKFLOW RESULTS")
        print("="*80)
        print(f"Status: {result['status']}")
        print(f"Success: {result['metadata']['success']}")
        print(f"Execution Time: {result['metadata']['execution_time']:.2f}s")
        print(f"Workflow: {result['metadata'].get('workflow_name', 'N/A')} v{result['metadata'].get('workflow_version', 'N/A')}")
        
        if result['metadata']['success']:
            print(f"\n📝 Final Response:")
            print(result['content'])
        else:
            print(f"\n❌ Error: {result['metadata'].get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in flexible workflow main: {str(e)}", exc_info=True)
        return {
            "status": WorkflowStatus.FAILED,
            "metadata": {"error": str(e), "success": False}
        }


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result["metadata"]["success"]:
            print("\n✅ Flexible Workflow completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Flexible Workflow failed: {result['metadata'].get('error')}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Flexible workflow interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in flexible workflow: {str(e)}", exc_info=True)
        sys.exit(1) 